# depanalyzer/parsers/c/code_parser.py
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import re
import logging

from base.base import BaseCodeParser, normalize_node_id
from utils.graph import GraphManager

log = logging.getLogger(__name__)

# Try to import tree-sitter C bindings. If unavailable, we'll fallback to regex.
_TREE_SITTER_AVAILABLE = True
try:
    import tree_sitter_c as tsc  # as user example suggests
    from tree_sitter import Language, Parser, Query, QueryCursor
    # Build language the way your environment exposes it (user example: tsc.language())
    C_LANGUAGE = Language(tsc.language())
except Exception as e:
    log.debug("tree-sitter C import failed, falling back to regex. (%s)", e)
    _TREE_SITTER_AVAILABLE = False

INCLUDE_QUERY = r"""
(preproc_include
  path: [
    (string_literal)
    (system_lib_string)
  ] @path)
"""

# Regex fallback: match #include "..." or #include <...>
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]', flags=re.MULTILINE)


# DEPRECATED: 使用base.py中的normalize_node_id替代
# def normalize_code_path(file_path: Path, repo_root: str) -> str:


def normalize_include_path(include_name: str, source_file: Path, repo_root: str) -> str:
    """Generate normalized path ID for included files"""
    repo_path = Path(repo_root)
    
    # System includes (angle brackets) - treat as system headers
    if include_name.startswith('/') or include_name in ['stdio.h', 'stdlib.h', 'string.h', 'unistd.h', 'fcntl.h', 'sys/stat.h', 'errno.h']:
        return f"//system:{include_name}"
    
    # Try to resolve relative includes
    if include_name.startswith('./') or include_name.startswith('../'):
        try:
            resolved_path = (source_file.parent / include_name).resolve()
            if resolved_path.is_file() and resolved_path.is_relative_to(repo_path):
                rel_path = resolved_path.relative_to(repo_path)
                return f"//{rel_path.as_posix()}"
        except (ValueError, OSError):
            pass
    
    # Look for the include file in common include directories
    potential_paths = [
        source_file.parent / include_name,
        repo_path / include_name,
        repo_path / "include" / include_name,
        repo_path / "src" / include_name,
    ]
    
    for potential_path in potential_paths:
        try:
            if potential_path.is_file() and potential_path.is_relative_to(repo_path):
                rel_path = potential_path.relative_to(repo_path)
                return f"//{rel_path.as_posix()}"
        except (ValueError, OSError):
            continue
    
    # Default: treat as project-relative include
    return f"//include:{include_name}"

class CodeParser(BaseCodeParser):
    NAME = "c"
    # files this parser cares about - include both C and C++ extensions
    CODE_GLOBS = ["**/*.c", "**/*.cpp", "**/*.cxx", "**/*.cc", "**/*.C", 
                  "**/*.h", "**/*.hpp", "**/*.hxx", "**/*.hh", "**/*.H",
                  "**/*.i", "**/*.S"]

    def __init__(self, repo_root: str, shared_graph=None) -> None:
        super().__init__(repo_root, shared_graph)

    def parse_file(self, file_path: Path, shared_graph: GraphManager) -> None:
        """
        Parse a single C source/header file and update the shared graph with:
          - a node for the source file (type="code")
          - nodes for each included path (type="header")
          - edges src -> header with label="include"
        """
        # Generate standardized paths
        source_id = normalize_node_id(file_path, self.repo_root)
        src_path = str(file_path.resolve())
        
        # Create and add the source node with new format
        src = shared_graph.create_vertex(
            source_id,
            parser_name=self.NAME,
            type="code",
            src_path=src_path,
            id=source_id
        )
        shared_graph.add_node(src)

        try:
            raw = file_path.read_bytes()
        except Exception as exc:
            log.warning("Failed reading %s: %s", file_path, exc)
            return

        includes: List[str] = []

        if _TREE_SITTER_AVAILABLE:
            try:
                parser = Parser(C_LANGUAGE)
                tree = parser.parse(raw)
                query = Query(C_LANGUAGE, INCLUDE_QUERY)
                cursor = QueryCursor(query)

                for match in cursor.matches(tree.root_node):
                    captures = match[1]  # This is a dict: {'capture_name': [nodes]}
                    for capture_name, nodes in captures.items():
                        if capture_name == "path":
                            for node in nodes:
                                try:
                                    text = node.text.decode("utf8").strip('"<>')
                                    if text:
                                        includes.append(text)
                                except Exception:
                                    # best-effort: ignore node that cannot decode
                                    continue
            except Exception as exc:
                # If any tree-sitter step fails, fallback to regex
                log.debug("tree-sitter parse/query failed for %s: %s. Falling back to regex.", file_path, exc)
                includes = INCLUDE_RE.findall(raw.decode("utf8", errors="ignore"))
        else:
            # regex fallback
            try:
                text = raw.decode("utf8", errors="ignore")
                includes = INCLUDE_RE.findall(text)
            except Exception:
                includes = []

        # Deduplicate includes while preserving order
        seen = set()
        uniq_includes = []
        for inc in includes:
            if inc not in seen:
                uniq_includes.append(inc)
                seen.add(inc)

        # Add header nodes and edges
        for inc in uniq_includes:
            # Generate standardized target path for the include
            target_id = normalize_include_path(inc, file_path, self.repo_root)
            
            # Determine header type based on target path
            if target_id.startswith("//system:"):
                header_type = "system_header"
            elif target_id.startswith("//include:"):
                header_type = "project_header"
            else:
                header_type = "code"  # Actual source file being included
            
            # Create header vertex with new format (only if it doesn't already exist)
            # Note: We don't set src_path for headers since they might not physically exist
            header_v = shared_graph.create_vertex(
                target_id,
                parser_name=self.NAME,
                type=header_type,
                id=target_id
            )
            shared_graph.add_node(header_v)
            
            # Create edge with new format using label instead of type
            edge = shared_graph.create_edge(
                source_id,
                target_id,
                parser_name=self.NAME,
                label="include"
            )
            shared_graph.add_edge(edge)
