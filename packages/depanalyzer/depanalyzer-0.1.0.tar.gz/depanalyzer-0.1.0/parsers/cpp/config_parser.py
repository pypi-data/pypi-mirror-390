# depanalyzer/parsers/cmake/config_parser.py
from __future__ import annotations
from pathlib import Path
import os
from typing import Optional, Iterable, List, Tuple
import re
import logging

from lark import Lark, Tree, Token

from base.base import BaseConfigParser, normalize_node_id
from utils.graph import GraphManager, Triple

log = logging.getLogger(__name__)

# ---------- Grammar (use the grammar you provided) ----------
CMAKE_GRAMMAR = r"""
start: file

file          : (_file_element newline_or_gap)* _file_element
_file_element : command_element
              | non_command_element
              | block
              | preformatted_block

?command_element    : command_invocation [line_comment]
non_command_element : bracket_comment* [line_comment]

preformatted_block : DISABLE_FORMATTER PREFORMATTED_LINE* ENABLE_FORMATTER

?newline_or_gap : NEWLINE+

DISABLE_FORMATTER : "# gersemi: off"
ENABLE_FORMATTER  : "# gersemi: on"
PREFORMATTED_LINE : /(?:(?!( |\t)*# gersemi: on))( |\t|.)*\n/

block      : _foreach_block
           | _function_block
           | _if_block
           | _macro_block
           | _while_block
           | _block_block
block_body : (newline_or_gap _file_element)* newline_or_gap

command_template{term}: term _invocation_part -> command_invocation
element_template{term}: command_template{term} [line_comment] -> command_element

_block_template{start_term, end_term}: element_template{start_term} block_body element_template{end_term}
_block_block    : _block_template{BLOCK, ENDBLOCK}
_foreach_block  : _block_template{FOREACH, ENDFOREACH}
_function_block : _block_template{FUNCTION, ENDFUNCTION}

_if_block       : element_template{IF}     block_body [_alternatives] element_template{ENDIF}
_alternatives   : _elseif_clause* [_else_clause]
_elseif_clause  : element_template{ELSEIF} block_body
_else_clause    : element_template{ELSE}   block_body

_macro_block    : _block_template{MACRO, ENDMACRO}
_while_block    : _block_template{WHILE, ENDWHILE}

BLOCK       : "block"i
ELSE        : "else"i
ELSEIF      : "elseif"i
ENDBLOCK    : "endblock"i
ENDFOREACH  : "endforeach"i
ENDFUNCTION : "endfunction"i
ENDIF       : "endif"i
ENDMACRO    : "endmacro"i
ENDWHILE    : "endwhile"i
FOREACH     : "foreach"i
FUNCTION    : "function"i
IF          : "if"i
MACRO       : "macro"i
WHILE       : "while"i

command_invocation  : IDENTIFIER _invocation_part
_invocation_part    : [_SPACE] LEFT_PARENTHESIS arguments RIGHT_PARENTHESIS
IDENTIFIER          : /[A-Za-z_][A-Za-z0-9_]*/
arguments           : (commented_argument | _separation)*
_separation         : _separation_atom+
_separation_atom    : bracket_comment
                    | [line_comment] NEWLINE

?commented_argument : argument [(line_comment NEWLINE | bracket_comment)]

?argument : bracket_argument
          | quoted_argument
          | unquoted_argument
          | complex_argument

bracket_argument : /\[(?P<equal_signs>(=*))\[([\s\S]+?)\](?P=equal_signs)\]/

quoted_argument     : QUOTATION_MARK QUOTED_ELEMENT* QUOTATION_MARK
QUOTED_ELEMENT      : /([^\\\"]|\n)+/
                    | ESCAPE_SEQUENCE
                    | QUOTED_CONTINUATION
QUOTED_CONTINUATION : BACKSLASH NEWLINE

unquoted_argument : UNQUOTED_ARGUMENT
UNQUOTED_ARGUMENT : UNQUOTED_ELEMENT+
UNQUOTED_ELEMENT  : /(?:(?!\[=*\[))[^\$\s\(\)#\"\\]+/
                  | /(?:(?!\[=*\[))[^\s\(\)#\"\\]/
                  | ESCAPE_SEQUENCE
                  | MAKE_STYLE_REFERENCE

MAKE_STYLE_REFERENCE : /\$\([^\)\n\"#]+?\)/

complex_argument : LEFT_PARENTHESIS arguments RIGHT_PARENTHESIS

ESCAPE_SEQUENCE: /\\([^A-Za-z0-9]|[nrt])/

bracket_comment : _POUND_SIGN bracket_argument
line_comment    : _POUND_SIGN [LINE_COMMENT_CONTENT]
LINE_COMMENT_CONTENT : /[^\n]+/

BACKSLASH              : "\\\\"
LEFT_PARENTHESIS       : "("
NEWLINE                : "\\n"
_POUND_SIGN            : "#"
QUOTATION_MARK         : "\""
RIGHT_PARENTHESIS      : ")"
_SPACE                 : /[ \\t]+/

%ignore _SPACE
"""

# ---------- Helper regex to tokenize argument string ----------
# Try to match bracket-argument [[...]] (with optional = signs), quoted "...", or unquoted token.
_TOKEN_RE = re.compile(
    r"""
    (\[(=*)\[(?:.|\n)*?\]\2\])   # bracket-style [[...]] with optional = signs
    |("(?:(?:\\.|[^"\\])*)")     # double-quoted string with escapes
    |('(?:(?:\\.|[^'\\])*)')     # single-quoted (rare in cmake but safe)
    |([^\s()#]+)                 # unquoted token (stop at whitespace, parentheses, #)
    """,
    re.VERBOSE,
)

# CMake keywords that should not be treated as dependencies
CMAKE_KEYWORDS = {
    "PUBLIC", "PRIVATE", "INTERFACE", 
    "STATIC", "SHARED", "MODULE", "OBJECT",
    "IMPORTED", "ALIAS", "EXCLUDE_FROM_ALL",
    "OPTIONAL", "REQUIRED", "QUIET", "COMPONENTS"
}

# Common English words that shouldn't be treated as dependencies
# These often come from comments that weren't properly filtered
COMMON_WORDS = {
    "THE", "TO", "A", "AN", "AND", "OR", "FOR", "IN", "ON", "AT", "BY", "WITH",
    "FROM", "AS", "IS", "ARE", "WAS", "WERE", "BE", "BEEN", "BEING", "HAVE", "HAS", "HAD",
    "DO", "DOES", "DID", "WILL", "WOULD", "COULD", "SHOULD", "MAY", "MIGHT", "CAN",
    "THIS", "THAT", "THESE", "THOSE", "YOU", "YOUR", "YOURS", "IT", "ITS", "HE", "HIS",
    "SHE", "HER", "HERS", "WE", "OUR", "OURS", "THEY", "THEIR", "THEIRS",
    "LIBRARY", "LIBRARIES", "TARGET", "LINK", "LINKS", "LINKED", "LINKING",
    "INCLUDED", "INCLUDE", "INCLUDES", "INCLUDING", "NDK", "CMAKE", "BUILD", "BUILDS",
    "FILE", "FILES", "PATH", "PATHS", "SOURCE", "SOURCES", "CODE", "CODES",
    "SPECIFIED", "SPECIFIES", "SPECIFY", "DEFINE", "DEFINES", "DEFINED",
    "MULTIPLE", "SUCH", "GRADLE", "AUTOMATICALLY", "PACKAGES", "SHARED",
    "RELATIVE", "PROVIDES", "PROVIDES", "SETS", "NAMES", "CREATES"
}

# Pattern to match CMake variables ${VAR_NAME}
CMAKE_VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')


class CMakeVariableResolver:
    """CMake variable resolver supporting basic variables and list operations"""
    
    def __init__(self, repo_root: str, cmake_file: Path):
        self.repo_root = Path(repo_root)
        self.cmake_file = cmake_file
        self.cmake_dir = cmake_file.parent
        self.project_name = None
        
        # Initialize common variables
        self.variables = {
            'CMAKE_SOURCE_DIR': str(self.repo_root),
            'CMAKE_CURRENT_SOURCE_DIR': str(self.cmake_dir),
            'CMAKE_CURRENT_BINARY_DIR': str(self.cmake_dir / 'build'),
            'CMAKE_CURRENT_LIST_DIR': str(self.cmake_dir),
            'PROJECT_SOURCE_DIR': str(self.repo_root),
            'PROJECT_BINARY_DIR': str(self.repo_root / 'build'),
        }
        # Lists that can be appended to
        self.lists = {}
        # FetchContent projects and their variables
        self.fetchcontent_projects = {}
    
    def set_project_name(self, name: str):
        """Set project name from project() command"""
        self.project_name = name
        self.variables['CMAKE_PROJECT_NAME'] = name
    
    def declare_fetchcontent_project(self, project_name: str, git_repository: str = "", git_tag: str = ""):
        """Declare a FetchContent project and set up its variables"""
        project_name_lower = project_name.lower()
        
        # In a real scenario, FetchContent would download to _deps directory
        # For simulation, we'll assume it's in a standard location
        deps_dir = self.cmake_dir / "_deps"
        project_source_dir = deps_dir / f"{project_name_lower}-src"
        project_binary_dir = deps_dir / f"{project_name_lower}-build"
        
        # Store project info
        self.fetchcontent_projects[project_name_lower] = {
            'name': project_name,
            'git_repository': git_repository,
            'git_tag': git_tag,
            'source_dir': str(project_source_dir),
            'binary_dir': str(project_binary_dir)
        }
        
        # Set the standard FetchContent variables
        self.variables[f'{project_name_lower}_SOURCE_DIR'] = str(project_source_dir)
        self.variables[f'{project_name_lower}_BINARY_DIR'] = str(project_binary_dir)
        
        # Also set uppercase versions (sometimes used)
        project_name_upper = project_name.upper()
        self.variables[f'{project_name_upper}_SOURCE_DIR'] = str(project_source_dir)
        self.variables[f'{project_name_upper}_BINARY_DIR'] = str(project_binary_dir)
        
        # Debug: log variable setting for quickjs
        if project_name_lower == 'quickjs':
            log.info(f"Set FetchContent variables for {project_name}:")
            log.info(f"  {project_name_lower}_SOURCE_DIR = {project_source_dir}")
            log.info(f"  {project_name_upper}_SOURCE_DIR = {project_source_dir}")
            log.info(f"All variables now: {list(self.variables.keys())}")
    
    def set_variable(self, name: str, value: str):
        """Set a variable from set() command"""
        self.variables[name] = value
    
    def append_to_list(self, list_name: str, items: list):
        """Append items to a CMake list variable"""
        if list_name not in self.lists:
            self.lists[list_name] = []
        self.lists[list_name].extend(items)
        # Also update as regular variable for ${VAR} resolution
        self.variables[list_name] = ';'.join(self.lists[list_name])  # CMake uses ; as separator
        
    def set_list(self, list_name: str, items: list):
        """Set a CMake list variable"""
        self.lists[list_name] = items[:]
        self.variables[list_name] = ';'.join(items)
        
    def get_list_items(self, list_name: str) -> list:
        """Get items from a CMake list variable"""
        return self.lists.get(list_name, [])
        
    def expand_list_variable(self, var_name: str) -> list:
        """Expand a list variable to its individual items"""
        # Remove ${} if present
        clean_var_name = var_name.strip('${}')
        result = self.get_list_items(clean_var_name)
        
        # Debug: log list variable expansion for sources (remove excessive logging)
        # if 'sources' in clean_var_name.lower():
        #     log.info(f"Expanding list variable: {clean_var_name}")
        #     log.info(f"  Items found: {len(result)}")
        #     for i, item in enumerate(result):
        #         log.info(f"    [{i}]: {item}")
        
        return result
        
    def glob_files(self, patterns: list) -> list:
        """Expand file glob patterns to actual file paths"""
        import glob
        files = []
        for pattern in patterns:
            log.info(f"  Processing glob pattern: {pattern}")
            # Resolve variables in pattern
            resolved_pattern = self.resolve(pattern)
            log.info(f"    After variable resolution: {resolved_pattern}")
            
            # Convert to absolute path if relative
            if not Path(resolved_pattern).is_absolute():
                resolved_pattern = str(self.cmake_dir / resolved_pattern)
                log.info(f"    Absolute pattern: {resolved_pattern}")
                
            # Use glob to find matching files
            matching_files = glob.glob(resolved_pattern)
            log.info(f"    Glob found {len(matching_files)} files: {matching_files}")
            
            # Convert back to paths relative to cmake_dir for consistency
            for file_path in matching_files:
                try:
                    rel_path = Path(file_path).relative_to(self.cmake_dir)
                    files.append(str(rel_path))
                except ValueError:
                    # If file is outside cmake_dir, use absolute path
                    files.append(file_path)
                    
        return files
    
    def resolve(self, var_expr: str) -> str:
        """Resolve ${VAR_NAME} expressions in strings, even when part of larger patterns"""
        # Handle simple case: entire string is a variable
        if var_expr.startswith('${') and var_expr.endswith('}'):
            var_name = var_expr[2:-1]  # Remove ${ and }
            
            # Debug: log resolution attempts for important variables (reduced logging)
            # if 'quickjs' in var_name.lower() or 'NATIVERENDER' in var_name.upper():
            #     log.info(f"Attempting to resolve simple variable: {var_name}")
            #     log.info(f"Available variables: {list(self.variables.keys())}")
            #     if var_name in self.variables:
            #         log.info(f"Found variable: {var_name} = {self.variables[var_name]}")
            #     else:
            #         log.info(f"Variable {var_name} NOT FOUND!")
            
            resolved = self.variables.get(var_name)
            if resolved is None:
                # 环境变量回退（用于如 OHOS_ARCH 等从工具链注入的变量）
                resolved = os.environ.get(var_name)
            if resolved is None:
                return var_expr
            
            # if 'quickjs' in var_name.lower() or 'NATIVERENDER' in var_name.upper():
            #     log.info(f"Resolution result: {var_expr} -> {resolved}")
            
            return resolved
        
        # Handle complex case: string contains variables mixed with other text
        # Use regex to find all ${VAR_NAME} patterns
        result = var_expr
        for match in CMAKE_VAR_PATTERN.finditer(var_expr):
            var_full = match.group(0)  # ${VAR_NAME}
            var_name = match.group(1)  # VAR_NAME
            
            # Debug: log resolution attempts for important variables (reduced logging)
            # if 'quickjs' in var_name.lower() or 'NATIVERENDER' in var_name.upper():
            #     log.info(f"Attempting to resolve embedded variable: {var_name} in: {var_expr}")
            #     log.info(f"Available variables: {list(self.variables.keys())}")
            #     if var_name in self.variables:
            #         log.info(f"Found variable: {var_name} = {self.variables[var_name]}")
            #     else:
            #         log.info(f"Variable {var_name} NOT FOUND!")
            
            if var_name in self.variables:
                replacement = self.variables[var_name]
                result = result.replace(var_full, replacement)
            else:
                env_val = os.environ.get(var_name)
                if env_val is not None:
                    result = result.replace(var_full, env_val)
                
                # if 'quickjs' in var_name.lower() or 'NATIVERENDER' in var_name.upper():
                #     log.info(f"Replaced {var_full} with {replacement} in: {result}")
        
        # Recursively resolve any remaining variables in the result
        # This handles cases like NATIVERENDER_ROOT_PATH = ${CMAKE_CURRENT_SOURCE_DIR}
        if result != var_expr and CMAKE_VAR_PATTERN.search(result):
            # Found more variables to resolve, recurse with a depth limit to prevent infinite loops
            if not hasattr(self, '_resolve_depth'):
                self._resolve_depth = 0
            
            self._resolve_depth += 1
            if self._resolve_depth < 10:  # Prevent infinite recursion
                resolved_result = self.resolve(result)
                self._resolve_depth -= 1
                
                if 'NATIVERENDER' in var_expr.upper() or 'CMAKE_CURRENT' in var_expr.upper():
                    log.info(f"Recursive resolution: {result} -> {resolved_result}")
                    
                return resolved_result
            else:
                self._resolve_depth -= 1
                log.warning(f"Max recursion depth reached resolving: {var_expr}")
        
        return result


# DEPRECATED: 使用base.py中的normalize_node_id替代
# def normalize_target_id(cmake_file: Path, target_name: str, repo_root: str) -> str:


def map_target_type(cmake_command: str, library_type: Optional[str] = None) -> str:
    """Map CMake command and library type to standardized type"""
    if cmake_command == "add_executable":
        return "executable"
    elif cmake_command == "add_library":
        if library_type == "SHARED":
            return "shared_library"
        elif library_type == "STATIC":
            return "static_library"
        elif library_type == "MODULE":
            return "module_library"
        elif library_type == "INTERFACE":
            return "interface_library"
        else:
            return "shared_library"  # Default for add_library without type
    else:
        return "library"


def _clean_cmake_token(token: str) -> str:
    """
    Clean a CMake token by:
    1. Removing surrounding quotes
    2. Resolving/marking variables
    3. Stripping whitespace
    """
    if not token:
        return token
    
    # Remove surrounding quotes
    token = token.strip()
    if (token.startswith('"') and token.endswith('"')) or \
       (token.startswith("'") and token.endswith("'")):
        token = token[1:-1]
    
    # For variables like ${VAR}, we can either:
    # 1. Keep them as variables (current approach)
    # 2. Try to resolve them if we have context
    # For now, we'll keep them but mark them as variables
    
    return token.strip()


def _is_valid_dependency(token: str) -> bool:
    """
    Check if a token represents a valid dependency (not a keyword, common word, or empty).
    """
    if not token or not token.strip():
        return False
    
    cleaned = _clean_cmake_token(token).upper()
    
    # Skip CMake keywords
    if cleaned in CMAKE_KEYWORDS:
        return False
    
    # Skip common English words (likely from comments)
    if cleaned in COMMON_WORDS:
        return False
    
    # Skip generator expressions like $<...>
    if token.strip().startswith('$<') and token.strip().endswith('>'):
        return False
    
    # Skip obviously invalid tokens
    if cleaned in {'', '(', ')', '{', '}', '$', '#'}:
        return False
    
    # Skip single characters and very short tokens that are likely noise
    if len(cleaned) <= 1:
        return False
    
    # Skip tokens that are just punctuation
    if cleaned.strip('.,;:!?-_+*=<>[]{}()') == '':
        return False
    
    return True


def _extract_dependencies_from_args(args: List[str], skip_first: int = 1) -> List[str]:
    """
    Extract valid dependencies from argument list, skipping CMake keywords.
    """
    if len(args) <= skip_first:
        return []
    
    dependencies = []
    i = skip_first
    
    while i < len(args):
        token = args[i]
        
        # Skip visibility specifiers and their following tokens
        if token.upper() in {"PUBLIC", "PRIVATE", "INTERFACE"}:
            i += 1
            continue
        
        # Clean and validate the token
        cleaned = _clean_cmake_token(token)
        if _is_valid_dependency(cleaned):
            dependencies.append(cleaned)
        
        i += 1
    
    return dependencies


def _extract_arg_tokens(arg_text: str) -> List[str]:
    """
    From inside the parentheses text, extract token list using regex.
    Keeps bracket-arguments, quoted strings, and unquoted tokens.
    Filters out comments and comment-related tokens.
    """
    # First, remove comment lines and inline comments
    clean_lines = []
    for line in arg_text.split('\n'):
        # Remove inline comments
        comment_pos = line.find('#')
        if comment_pos >= 0:
            line = line[:comment_pos]
        line = line.strip()
        if line:  # Only add non-empty lines
            clean_lines.append(line)
    
    cleaned_arg_text = ' '.join(clean_lines)
    
    tokens: List[str] = []
    for m in _TOKEN_RE.finditer(cleaned_arg_text):
        br = m.group(1)
        dq = m.group(3)
        sq = m.group(4)
        uq = m.group(5)
        if br:
            # remove surrounding [==[ and ]==]
            inner = re.sub(r'^\[(=*)\[', '', br)
            inner = re.sub(r'\](=*)\]$', '', inner)
            tokens.append(inner.strip())
        elif dq is not None:
            tokens.append(dq[1:-1])  # strip quotes
        elif sq is not None:
            tokens.append(sq[1:-1])
        elif uq:
            # Additional check to skip comment-like tokens
            if not uq.startswith('#'):
                tokens.append(uq)
    return tokens


# Create a Lark parser once (LALR is faster)
_PARSER = Lark(CMAKE_GRAMMAR, parser="lalr", propagate_positions=False, maybe_placeholders=False)


class ConfigParser(BaseConfigParser):
    NAME = "cmake"
    CONFIG_GLOBS = ["**/CMakeLists.txt", "**/*.cmake"]

    def parse_file(self, file_path: Path, shared_graph: GraphManager) -> None:
        """
        Parse a CMake file and update the shared graph with:
        - targets created by add_library/add_executable
        - link relationships from target_link_libraries
        - add_subdirectory results (as directory nodes)
        """
        try:
            text = file_path.read_text(encoding="utf8", errors="ignore")
        except Exception as e:
            log.warning("Failed to read %s: %s", file_path, e)
            return
        
        # Initialize variable resolver for this file
        variable_resolver = CMakeVariableResolver(self.repo_root, file_path)

        try:
            tree = _PARSER.parse(text)
        except Exception as e:
            log.debug("Lark parsing failed for %s: %s", file_path, e)
            # parsing failed — fall back to simple regex extraction of common commands
            self._fallback_regex_parse(text, shared_graph, variable_resolver, file_path)
            return

        # Walk parse tree for command_invocation
        for cmd in tree.find_data("command_invocation"):
            # A command_invocation in this grammar: IDENTIFIER then _invocation_part
            # Typically cmd.children[0] is IDENTIFIER (Token)
            if not cmd.children:
                continue
            ident = cmd.children[0]
            if not isinstance(ident, Token):
                continue
            cmd_name = str(ident).lower()
            original_cmd_name = str(ident)

            # Extract argument text by slicing original source between "(" and ")"
            # cmd.pretty positions are not propagated, so we'll reconstruct text from tree children.
            # Find the text segment containing the parentheses by converting this subtree to string
            cmd_text = "".join([str(c) for c in cmd.children[1:]]) if len(cmd.children) > 1 else ""
            # cmd_text may contain tokens and parentheses; try to extract inside (...)
            m = re.search(r"\((.*)\)\s*$", cmd_text, flags=re.DOTALL)
            arg_text = m.group(1) if m else ""

            args = _extract_arg_tokens(arg_text)
            
            # Debug: Log all commands for FetchContent related ones
            if "fetchcontent" in cmd_name or "fetch" in cmd_name:
                log.info(f"Found command: {original_cmd_name} -> {cmd_name} with args: {args}")
            
            # Handle project() command to set project name
            if cmd_name == "project" and args:
                project_name = _clean_cmake_token(args[0])
                if project_name:
                    variable_resolver.set_project_name(project_name)
                continue
            
            # Handle FetchContent_Declare() command
            if cmd_name == "fetchcontent_declare" and args:
                project_name = _clean_cmake_token(args[0])
                log.debug(f"Found FetchContent_Declare for project: {project_name}")
                if project_name:
                    # Extract optional parameters like GIT_REPOSITORY and GIT_TAG
                    git_repository = ""
                    git_tag = ""
                    
                    # Look for GIT_REPOSITORY and GIT_TAG in the arguments
                    i = 1
                    while i < len(args) - 1:
                        arg = args[i].upper()
                        if arg == "GIT_REPOSITORY" and i + 1 < len(args):
                            git_repository = _clean_cmake_token(args[i + 1])
                            i += 2
                        elif arg == "GIT_TAG" and i + 1 < len(args):
                            git_tag = _clean_cmake_token(args[i + 1])
                            i += 2
                        else:
                            i += 1
                    
                    log.debug(f"Declaring FetchContent project: {project_name} (repo: {git_repository}, tag: {git_tag})")
                    variable_resolver.declare_fetchcontent_project(project_name, git_repository, git_tag)
                continue
                
            # Handle FetchContent_MakeAvailable() command - this activates the declared project
            if cmd_name == "fetchcontent_makeavailable" and args:
                for arg in args:
                    project_name = _clean_cmake_token(arg)
                    if project_name:
                        log.debug(f"Making available FetchContent project: {project_name}")
                        # The project should already be declared, this just confirms it's available
                        continue
            
            # Handle set() command to set variables or lists
            if cmd_name == "set" and len(args) >= 2:
                var_name = _clean_cmake_token(args[0])
                if var_name:
                    if len(args) == 2:
                        # Single value: set(VAR value)
                        var_value = _clean_cmake_token(args[1])
                        if var_value:
                            variable_resolver.set_variable(var_name, var_value)
                    else:
                        # Multiple values: set(VAR value1 value2 ...) - treat as list
                        items = []
                        for item in args[1:]:
                            clean_item = _clean_cmake_token(item)
                            if clean_item and _is_valid_dependency(clean_item):
                                items.append(clean_item)
                        if items:
                            variable_resolver.set_list(var_name, items)
                continue
            
            # Handle list(APPEND ...) command to append to list variables
            if cmd_name == "list" and len(args) >= 3:
                list_op = args[0].upper()
                if list_op == "APPEND":
                    list_name = _clean_cmake_token(args[1])
                    if list_name:
                        # Extract all items to append (everything after the list name)
                        items_to_append = []
                        for item in args[2:]:
                            clean_item = _clean_cmake_token(item)
                            if clean_item and _is_valid_dependency(clean_item):
                                items_to_append.append(clean_item)
                        if items_to_append:
                            variable_resolver.append_to_list(list_name, items_to_append)
                continue
            
            # Handle file(GLOB ...) command to collect files matching patterns
            if cmd_name == "file" and len(args) >= 3:
                file_op = args[0].upper()
                if file_op == "GLOB":
                    var_name = _clean_cmake_token(args[1])
                    log.info(f"Processing file(GLOB) command for variable: {var_name}")
                    if var_name:
                        # Extract glob patterns (everything after the variable name)
                        patterns = []
                        for pattern in args[2:]:
                            clean_pattern = _clean_cmake_token(pattern)
                            if clean_pattern:
                                patterns.append(clean_pattern)
                        
                        log.info(f"  Glob patterns: {patterns}")
                        if patterns:
                            # Use glob_files to find matching files
                            matching_files = variable_resolver.glob_files(patterns)
                            log.info(f"  Found {len(matching_files)} files: {matching_files}")
                            # Set the variable to the list of found files
                            variable_resolver.set_list(var_name, matching_files)
                continue

            # Now handle commands of interest
            if cmd_name in ("add_library", "add_executable"):
                if not args:
                    continue
                target = _clean_cmake_token(args[0])
                if not target:
                    continue
                
                # Resolve variables in target name
                target = variable_resolver.resolve(target)
                    
                # Check for library type specification (STATIC/SHARED/MODULE/OBJECT/INTERFACE)
                lib_type = None
                source_start_idx = 1  # Default: sources start from index 1
                if len(args) >= 2 and args[1].upper() in ("STATIC", "SHARED", "MODULE", "OBJECT", "INTERFACE"):
                    lib_type = args[1].upper()
                    source_start_idx = 2  # Sources start from index 2 if type is specified
                
                # Generate standardized type and paths
                node_type = map_target_type(cmd_name, lib_type)
                target_id = normalize_node_id(file_path, self.repo_root, target)
                src_path = str(file_path.resolve())
                
                # Create target node
                v = shared_graph.create_vertex(
                    target_id,
                    parser_name=self.NAME,
                    type=node_type,
                    src_path=src_path,
                    id=target_id
                )
                shared_graph.add_node(v)
                
                # Process source files (everything after target name and optional type)
                source_files_raw = _extract_dependencies_from_args(args, skip_first=source_start_idx)
                
                # Expand list variables and resolve regular variables
                source_files = []
                for source_file in source_files_raw:
                    if source_file.startswith('${') and source_file.endswith('}'):
                        # Check if it's a list variable
                        var_name = source_file[2:-1]  # Remove ${ and }
                        list_items = variable_resolver.expand_list_variable(var_name)
                        if list_items:
                            # Resolve each item in the list
                            for item in list_items:
                                resolved_item = variable_resolver.resolve(item)
                                source_files.append(resolved_item)
                        else:
                            # Not a list variable, try regular variable resolution
                            resolved = variable_resolver.resolve(source_file)
                            if resolved != source_file:  # Variable was resolved
                                source_files.append(resolved)
                            # If not resolved, skip this variable
                    else:
                        # Regular source file or non-variable
                        source_files.append(source_file)
                
                for source_file in source_files:
                    # Additional variable resolution for nested cases
                    resolved_source = variable_resolver.resolve(source_file)
                    
                    # Generate source file path - assume relative to CMakeLists.txt directory
                    cmake_dir = file_path.parent
                    if resolved_source.startswith('/'):
                        # Absolute path
                        source_path = Path(resolved_source)
                    else:
                        # Relative path
                        source_path = cmake_dir / resolved_source
                    
                    # Generate standardized source ID
                    try:
                        if source_path.exists():
                            # File exists - use actual path
                            source_id = normalize_node_id(source_path, self.repo_root)
                        else:
                            # File doesn't exist - use CMake dir + filename
                            rel_source = cmake_dir.relative_to(Path(self.repo_root)) / resolved_source
                            source_id = f"//{rel_source.as_posix()}"
                            
                        # Additional variable resolution for the source_id path itself
                        # This handles cases where the path still contains unresolved variables
                        if '${' in source_id:
                            original_id = source_id
                            # Extract and resolve any remaining variables in the path
                            for var_match in CMAKE_VAR_PATTERN.finditer(source_id):
                                var_expr = var_match.group(0)  # ${VAR_NAME}
                                resolved_var = variable_resolver.resolve(var_expr)
                                source_id = source_id.replace(var_expr, resolved_var)
                            log.debug(f"Resolved source_id: {original_id} -> {source_id}")
                            
                    except (ValueError, OSError):
                        # Fallback for path resolution errors
                        source_id = f"//{cmake_dir.name}/{resolved_source}"
                        # Also try to resolve variables in fallback path
                        if '${' in source_id:
                            for var_match in CMAKE_VAR_PATTERN.finditer(source_id):
                                var_expr = var_match.group(0)
                                resolved_var = variable_resolver.resolve(var_expr)
                                source_id = source_id.replace(var_expr, resolved_var)
                    
                    # Create source node (if it doesn't exist)
                    source_node = shared_graph.create_vertex(
                        source_id,
                        parser_name=self.NAME,
                        type="code",
                        id=source_id
                    )
                    shared_graph.add_node(source_node)
                    
                    # Create edge: target -> source
                    edge = shared_graph.create_edge(
                        target_id,
                        source_id,
                        parser_name=self.NAME,
                        label="sources"
                    )
                    shared_graph.add_edge(edge)

            elif cmd_name == "target_link_libraries":
                # syntax: target_link_libraries(target <PRIVATE|PUBLIC|INTERFACE> lib1 lib2 ...)
                if len(args) < 2:
                    continue
                    
                target = _clean_cmake_token(args[0])
                if not target:
                    continue
                
                # Resolve variables in target name
                target = variable_resolver.resolve(target)
                
                # Extract valid library dependencies, filtering out keywords
                # First remove any potential comment content from args
                clean_args = []
                for arg in args:
                    # Skip arguments that are clearly from comments
                    if not arg or arg.startswith('#'):
                        continue
                    # Remove inline comments
                    comment_pos = arg.find('#')
                    if comment_pos >= 0:
                        arg = arg[:comment_pos].strip()
                    if arg:
                        clean_args.append(arg)
                
                libs = _extract_dependencies_from_args(clean_args, skip_first=1)
                
                if not libs:
                    continue
                
                # Generate source target ID
                source_id = normalize_node_id(file_path, self.repo_root, target)
                
                # Create library nodes and link edges
                for lib in libs:
                    # Resolve variables in library name
                    resolved_lib = variable_resolver.resolve(lib)
                    
                    # Determine target ID for the library
                    if resolved_lib.startswith('//'):
                        # Already a normalized path
                        target_id = resolved_lib
                    elif '::' in resolved_lib:
                        # Package imported target (e.g., mmkv::mmkv, PkgConfig::GTK)
                        target_id = f"//{resolved_lib}"
                    elif CMAKE_VAR_PATTERN.search(lib):
                        # Unresolved variable - keep original
                        target_id = lib
                    else:
                        # Regular library - assume it's in the same directory or system library
                        if resolved_lib.endswith(('.so', '.lib', '.dll', '.a')):
                            # System library file
                            target_id = f"//system:{resolved_lib}"
                        else:
                            # Assume same directory
                            target_id = normalize_node_id(file_path, self.repo_root, resolved_lib)
                    
                    # Create the edge with new format
                    e = shared_graph.create_edge(
                        source_id, 
                        target_id, 
                        parser_name=self.NAME,
                        label="link_libraries"
                    )
                    shared_graph.add_edge(e)

            elif cmd_name == "add_subdirectory":
                # add_subdirectory(dir [binary_dir] [EXCLUDE_FROM_ALL])
                if args:
                    sub = _clean_cmake_token(args[0])
                    if sub and _is_valid_dependency(sub):
                        resolved_sub = variable_resolver.resolve(sub)
                        sub_path = Path(self.repo_root) / resolved_sub
                        
                        # Create subdirectory node with new format
                        if sub_path.is_dir():
                            dir_id = f"//{resolved_sub}"
                            dir_v = shared_graph.create_vertex(
                                dir_id,
                                parser_name=self.NAME,
                                type="subdirectory",
                                src_path=str(sub_path.resolve()),
                                id=dir_id
                            )
                            shared_graph.add_node(dir_v)
                        
            elif cmd_name in ("include_directories", "link_libraries"):
                # These commands are less important for dependency analysis
                # Skip for now to keep output focused on target relationships
                continue

            # other commands can be extended similarly

    def _fallback_regex_parse(self, text: str, shared_graph: GraphManager, variable_resolver: CMakeVariableResolver, file_path: Path) -> None:
        """
        If Lark parsing fails, try to extract common commands via regex.
        This is a defensive fallback to avoid losing basic info.
        Uses the same filtering logic as the main parser.
        """
        # Extract project name first
        project_re = re.compile(r'project\s*\(\s*([A-Za-z0-9_${}\-.:]+)', flags=re.IGNORECASE)
        for m in project_re.finditer(text):
            project_name = _clean_cmake_token(m.group(1))
            if project_name:
                variable_resolver.set_project_name(project_name)
                break
        
        # Extract FetchContent_Declare commands with improved regex for multiline matching
        def _extract_balanced_parentheses_content(text: str, start_pos: int) -> str:
            """Extract content between balanced parentheses starting from start_pos"""
            if start_pos >= len(text) or text[start_pos] != '(':
                return ""
            
            paren_count = 1
            pos = start_pos + 1
            while pos < len(text) and paren_count > 0:
                if text[pos] == '(':
                    paren_count += 1
                elif text[pos] == ')':
                    paren_count -= 1
                pos += 1
            
            if paren_count == 0:
                return text[start_pos + 1:pos - 1]  # Exclude parentheses
            return ""
        
        # Find FetchContent_Declare commands with balanced parentheses
        fetchcontent_pattern = re.compile(r'FetchContent_Declare\s*\(', flags=re.IGNORECASE)
        for match in fetchcontent_pattern.finditer(text):
            paren_pos = match.end() - 1  # Position of the opening parenthesis
            full_args = _extract_balanced_parentheses_content(text, paren_pos)
            
            if full_args:
                # Extract project name (first argument)
                args_tokens = _extract_arg_tokens(full_args)
                if args_tokens:
                    project_name = _clean_cmake_token(args_tokens[0])
                    if project_name:
                        log.debug(f"Regex fallback found FetchContent_Declare: {project_name}")
                        
                        # Extract GIT_REPOSITORY and GIT_TAG
                        git_repository = ""
                        git_tag = ""
                        
                        git_repo_match = re.search(r'GIT_REPOSITORY\s+([^\s\n]+)', full_args, re.IGNORECASE)
                        if git_repo_match:
                            git_repository = _clean_cmake_token(git_repo_match.group(1))
                        
                        git_tag_match = re.search(r'GIT_TAG\s+([^\s\n]+)', full_args, re.IGNORECASE)
                        if git_tag_match:
                            git_tag = _clean_cmake_token(git_tag_match.group(1))
                        
                        log.debug(f"Regex declaring FetchContent project: {project_name} (repo: {git_repository}, tag: {git_tag})")
                        variable_resolver.declare_fetchcontent_project(project_name, git_repository, git_tag)
        
        # Extract set() commands for variable/list resolution  
        set_re = re.compile(r'set\s*\(\s*([A-Za-z0-9_${}\-.:]+)([^)]+)\)', flags=re.IGNORECASE | re.DOTALL)
        for m in set_re.finditer(text):
            var_name = _clean_cmake_token(m.group(1))
            args_text = m.group(2)
            if var_name:
                items = _extract_arg_tokens(args_text)
                clean_items = []
                for item in items:
                    clean_item = _clean_cmake_token(item)
                    if clean_item:
                        clean_items.append(clean_item)
                
                if len(clean_items) == 1:
                    # Single value
                    variable_resolver.set_variable(var_name, clean_items[0])
                elif len(clean_items) > 1:
                    # Multiple values - treat as list
                    valid_items = [item for item in clean_items if _is_valid_dependency(item)]
                    if valid_items:
                        variable_resolver.set_list(var_name, valid_items)
        
        # Extract list(APPEND ...) commands for variable resolution
        list_append_re = re.compile(r'list\s*\(\s*APPEND\s+([A-Za-z0-9_${}\-.:]+)([^)]+)\)', flags=re.IGNORECASE | re.DOTALL)
        for m in list_append_re.finditer(text):
            list_name = _clean_cmake_token(m.group(1))
            args_text = m.group(2)
            if list_name:
                # Parse the items to append
                items = _extract_arg_tokens(args_text)
                items_to_append = []
                for item in items:
                    clean_item = _clean_cmake_token(item)
                    if clean_item and _is_valid_dependency(clean_item):
                        items_to_append.append(clean_item)
                if items_to_append:
                    variable_resolver.append_to_list(list_name, items_to_append)
        
        # Extract file(GLOB ...) commands for file collection
        file_glob_re = re.compile(r'file\s*\(\s*GLOB\s+([A-Za-z0-9_${}\-.:]+)([^)]+)\)', flags=re.IGNORECASE | re.DOTALL)
        for m in file_glob_re.finditer(text):
            var_name = _clean_cmake_token(m.group(1))
            args_text = m.group(2)
            if var_name:
                patterns = _extract_arg_tokens(args_text)
                clean_patterns = []
                for pattern in patterns:
                    clean_pattern = _clean_cmake_token(pattern)
                    if clean_pattern:
                        clean_patterns.append(clean_pattern)
                
                if clean_patterns:
                    matching_files = variable_resolver.glob_files(clean_patterns)
                    variable_resolver.set_list(var_name, matching_files)
        
        def _extract_balanced_parentheses(text: str, start_pos: int) -> str:
            """Extract content between balanced parentheses starting from start_pos"""
            if start_pos >= len(text) or text[start_pos] != '(':
                return ""
            
            paren_count = 1
            pos = start_pos + 1
            while pos < len(text) and paren_count > 0:
                if text[pos] == '(':
                    paren_count += 1
                elif text[pos] == ')':
                    paren_count -= 1
                pos += 1
            
            if paren_count == 0:
                return text[start_pos + 1:pos - 1]  # 排除括号本身
            return ""

        def _find_cmake_commands(pattern: str, text: str):
            """Find all CMake commands with balanced parentheses"""
            results = []
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start_pos = match.start()
                # 找到开括号
                paren_pos = text.find('(', start_pos)
                if paren_pos != -1:
                    # 提取目标名
                    target_match = re.match(r'\s*([A-Za-z0-9_${}\-.:]+)', text[paren_pos + 1:])
                    if target_match:
                        target_name = target_match.group(1)
                        # 提取平衡括号内的完整内容
                        full_content = _extract_balanced_parentheses(text, paren_pos)
                        if full_content:
                            # 移除目标名，得到参数部分
                            args_start = len(target_name)
                            while args_start < len(full_content) and full_content[args_start].isspace():
                                args_start += 1
                            args_text = full_content[args_start:]
                            results.append((target_name, args_text))
            return results

        # Use the improved command finder
        add_lib_commands = _find_cmake_commands(r'add_library\s*\(', text)
        add_exe_commands = _find_cmake_commands(r'add_executable\s*\(', text)
        tlink_re = re.compile(r'target_link_libraries\s*\(\s*([A-Za-z0-9_${}\-.:]+)\s+([^\)]+)\)', flags=re.IGNORECASE | re.DOTALL)

        def _process_cmake_target(target_name: str, args_text: str, command_type: str):
            """Helper to process add_library/add_executable commands with source file handling"""
            target = _clean_cmake_token(target_name)
            if not target or not _is_valid_dependency(target):
                return
            
            # Resolve variables in target name
            target = variable_resolver.resolve(target)
            
            # Parse arguments (type + source files)
            args_list = _extract_arg_tokens(args_text)
            
            # Determine library type and source start index
            lib_type = None
            source_start_idx = 0
            if args_list and args_list[0].upper() in {"STATIC", "SHARED", "MODULE", "OBJECT", "INTERFACE"}:
                lib_type = args_list[0].upper()
                source_start_idx = 1
            
            # Generate target node
            node_type = map_target_type(command_type, lib_type)
            target_id = normalize_node_id(file_path, self.repo_root, target)
            src_path = str(file_path.resolve())
            
            v = shared_graph.create_vertex(
                target_id,
                parser_name=self.NAME,
                type=node_type,
                src_path=src_path,
                id=target_id
            )
            shared_graph.add_node(v)
            
            # Process source files with list variable expansion
            source_files_raw = _extract_dependencies_from_args(args_list, skip_first=source_start_idx)
            
            # Expand list variables and resolve regular variables
            source_files = []
            for source_file in source_files_raw:
                if source_file.startswith('${') and source_file.endswith('}'):
                    # Check if it's a list variable
                    var_name = source_file[2:-1]  # Remove ${ and }
                    list_items = variable_resolver.expand_list_variable(var_name)
                    if list_items:
                        # Resolve each item in the list
                        for item in list_items:
                            resolved_item = variable_resolver.resolve(item)
                            source_files.append(resolved_item)
                    else:
                        # Not a list variable, try regular variable resolution
                        resolved = variable_resolver.resolve(source_file)
                        if resolved != source_file:  # Variable was resolved
                            source_files.append(resolved)
                        # If not resolved, skip this variable
                else:
                    # Regular source file or non-variable
                    source_files.append(source_file)
            
            for source_file in source_files:
                # Additional variable resolution for nested cases
                resolved_source = variable_resolver.resolve(source_file)
                
                # Generate source file path - assume relative to CMakeLists.txt directory
                cmake_dir = file_path.parent
                if resolved_source.startswith('/'):
                    source_path = Path(resolved_source)
                else:
                    source_path = cmake_dir / resolved_source
                
                # Generate standardized source ID
                try:
                    if source_path.exists():
                        source_id = normalize_node_id(source_path, self.repo_root)
                    else:
                        rel_source = cmake_dir.relative_to(Path(self.repo_root)) / resolved_source
                        source_id = f"//{rel_source.as_posix()}"
                        
                    # Additional variable resolution for the source_id path itself
                    if '${' in source_id:
                        original_id = source_id
                        for var_match in CMAKE_VAR_PATTERN.finditer(source_id):
                            var_expr = var_match.group(0)  # ${VAR_NAME}
                            resolved_var = variable_resolver.resolve(var_expr)
                            source_id = source_id.replace(var_expr, resolved_var)
                        log.debug(f"Fallback resolved source_id: {original_id} -> {source_id}")
                        
                except (ValueError, OSError):
                    source_id = f"//{cmake_dir.name}/{resolved_source}"
                    # Also try to resolve variables in fallback path
                    if '${' in source_id:
                        for var_match in CMAKE_VAR_PATTERN.finditer(source_id):
                            var_expr = var_match.group(0)
                            resolved_var = variable_resolver.resolve(var_expr)
                            source_id = source_id.replace(var_expr, resolved_var)
                
                # Create source node
                source_node = shared_graph.create_vertex(
                    source_id,
                    parser_name=self.NAME,
                    type="code",
                    id=source_id
                )
                shared_graph.add_node(source_node)
                
                # Create edge: target -> source
                edge = shared_graph.create_edge(
                    target_id,
                    source_id,
                    parser_name=self.NAME,
                    label="sources"
                )
                shared_graph.add_edge(edge)

        # Process add_library commands
        for target_name, args_text in add_lib_commands:
            _process_cmake_target(target_name, args_text, "add_library")
            
        # Process add_executable commands  
        for target_name, args_text in add_exe_commands:
            _process_cmake_target(target_name, args_text, "add_executable")
            
        # Process target_link_libraries commands
        for m in tlink_re.finditer(text):
            target = _clean_cmake_token(m.group(1))
            if not target or not _is_valid_dependency(target):
                continue
            
            # Resolve variables in target name
            target = variable_resolver.resolve(target)
                
            libs_text = m.group(2).strip()
            
            # Remove comments from the libs_text first
            # Split by lines and remove comment lines or comment parts
            cleaned_lines = []
            for line in libs_text.split('\n'):
                # Remove inline comments
                comment_pos = line.find('#')
                if comment_pos >= 0:
                    line = line[:comment_pos]
                line = line.strip()
                if line:  # Only add non-empty lines
                    cleaned_lines.append(line)
            
            cleaned_libs_text = ' '.join(cleaned_lines)
            
            # Split by whitespace but be more careful about quoted strings
            raw_libs = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', cleaned_libs_text)
            
            # Filter out keywords and clean the libraries
            valid_libs = []
            for lib in raw_libs:
                cleaned = _clean_cmake_token(lib)
                if _is_valid_dependency(cleaned):
                    valid_libs.append(cleaned)
                    
            if not valid_libs:
                continue
            
            # Generate source target ID
            source_id = normalize_node_id(file_path, self.repo_root, target)
                
            for lib in valid_libs:
                # Resolve variables in library name
                resolved_lib = variable_resolver.resolve(lib)
                
                # Determine target ID for the library (same logic as main parser)
                if resolved_lib.startswith('//'):
                    target_id = resolved_lib
                elif '::' in resolved_lib:
                    target_id = f"//{resolved_lib}"
                elif CMAKE_VAR_PATTERN.search(lib):
                    target_id = lib
                else:
                    if resolved_lib.endswith(('.so', '.lib', '.dll', '.a')):
                        target_id = f"//system:{resolved_lib}"
                    else:
                        target_id = normalize_node_id(file_path, self.repo_root, resolved_lib)
                
                # 针对库目标，尽量创建/补全库节点并推断类型
                lib_type = None
                lib_label = target_id
                src_path = None
                guessed_type = None

                # 基于文件后缀推断
                if any(target_id.endswith(ext) for ext in (".a", ".lib", ".dll")):
                    guessed_type = "static_library" if target_id.endswith(".a") else "shared_library"
                elif target_id.endswith(".so") or ".so." in target_id:
                    guessed_type = "shared_library"

                # 变量替换以获取更真实的路径
                resolved_target_id = target_id
                if CMAKE_VAR_PATTERN.search(resolved_target_id):
                    for m in CMAKE_VAR_PATTERN.finditer(resolved_target_id):
                        var_expr = m.group(0)
                        resolved = variable_resolver.resolve(var_expr)
                        if resolved != var_expr:
                            resolved_target_id = resolved_target_id.replace(var_expr, resolved)

                # 如果替换后变成绝对/相对路径，则设置 src_path 并用标准化ID
                try:
                    if resolved_target_id.startswith('/'):
                        src_path = resolved_target_id
                        lib_label = normalize_node_id(Path(resolved_target_id), self.repo_root)
                    else:
                        # 相对路径，按当前CMake目录解析
                        rp = (file_path.parent / resolved_target_id).resolve()
                        if rp.exists():
                            src_path = str(rp)
                            lib_label = normalize_node_id(rp, self.repo_root)
                except Exception:
                    pass

                # 确保节点存在，并补充类型/路径
                lib_node_data = shared_graph.query_node_by_label(lib_label)
                if lib_node_data is None:
                    lib_node = shared_graph.create_vertex(
                        lib_label,
                        parser_name=self.NAME,
                        type=guessed_type or "shared_library",
                        src_path=src_path,
                        id=lib_label,
                    )
                    shared_graph.add_node(lib_node)
                else:
                    # 回填缺失属性
                    if guessed_type and not lib_node_data.get("type"):
                        lib_node_data["type"] = guessed_type
                    if src_path and not lib_node_data.get("src_path"):
                        lib_node_data["src_path"] = src_path

                # 创建依赖边（边label后续导出会统一为 dep）
                e = shared_graph.create_edge(
                    source_id,
                    lib_label,
                    parser_name=self.NAME,
                    label="link_libraries",
                )
                shared_graph.add_edge(e)
