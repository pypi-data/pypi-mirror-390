import traceback
from pathlib import Path
from typing import Optional, Set

from tree_sitter import Language, Parser, Query, QueryCursor
from base.base import BaseCodeParser, normalize_node_id
from utils.graph import GraphManager, Vertex, Edge

# --- Tree-sitter Language Setup ---
try:
    import tree_sitter_typescript as tst
    TS_LANGUAGE = Language(tst.language_typescript())
except (ImportError, OSError, TypeError) as e:
    print(f"FATAL: Could not load tree-sitter-typescript language: {e}")
    TS_LANGUAGE = None

class CodeParser(BaseCodeParser):
    NAME = "hvigor"
    CODE_GLOBS = ["**/*.ets", "**/*.ts"]

    def __init__(self, repo_root: str, shared_graph: GraphManager):
        super().__init__(repo_root, shared_graph)
        if not TS_LANGUAGE:
            raise RuntimeError("ArkTS CodeParser cannot be initialized: tree-sitter language failed to load.")
        
        query_string = """
            (import_statement source: (string) @path)
            (export_statement source: (string) @path)
        """
        self.dependency_query = Query(TS_LANGUAGE, query_string)

    def parse_file(self, file_path: Path, shared_graph: GraphManager) -> None:
        """
        Parses a single source file, adding it and its dependencies as 'code' nodes
        with the unified format, and creates 'import' edges between them.
        """
        source_id = normalize_node_id(file_path, self.repo_root)
        
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            
            ts_parser = Parser(TS_LANGUAGE)
            tree = ts_parser.parse(content)
            
            cursor = QueryCursor(self.dependency_query)
            capture_dict = cursor.captures(tree.root_node)
            
            dependencies: Set[str] = set()
            if 'path' in capture_dict:
                for node in capture_dict['path']:
                    dep_str = node.text.decode('utf8').strip('"\'')
                    if dep_str.startswith("@ohos"):
                        continue
                    resolved_path = self._resolve_dependency(file_path, dep_str)
                    if resolved_path and resolved_path.is_file():
                        dep_id = normalize_node_id(resolved_path, self.repo_root)
                        dependencies.add(dep_id)

            with self.graph_lock:
                shared_graph.add_node(Vertex(
                    label=source_id, id=source_id, 
                    src_path=str(file_path.resolve()), type="code", 
                    parser_name=self.NAME
                ))

                for dep_id in dependencies:
                    # 从ID反向解析出路径用于src_path
                    dep_path = dep_id.replace('//', '')
                    if ':' not in dep_path:  # 普通文件路径
                        dep_abs_path = Path(self.repo_root) / dep_path
                        shared_graph.add_node(Vertex(
                            label=dep_id, id=dep_id, 
                            src_path=str(dep_abs_path.resolve()), type="code", 
                            parser_name=self.NAME
                        ))
                        shared_graph.add_edge(Edge(
                            u=source_id, v=dep_id, 
                            type="import", parser_name=self.NAME
                        ))

        except Exception as e:
            error_msg = f"Error parsing file {file_path}: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)

    def _resolve_dependency(self, source_file: Path, dep_str: str) -> Optional[Path]:
        """Resolves a dependency string to an absolute file path."""
        project_root = Path(self.repo_root)
        
        if dep_str.startswith(("./", "../")):
            resolved = (source_file.parent / dep_str).resolve()
            for ext in [".ets", ".ts", ".js"]:
                if (resolved.with_suffix(ext)).is_file():
                    return resolved.with_suffix(ext)
            if resolved.is_dir():
                for ext in [".ets", ".ts", ".js"]:
                    if (resolved / f"index{ext}").is_file():
                        return resolved / f"index{ext}"
            return None
        else:
            possible_path = project_root / dep_str
            for ext in [".ets", ".ts", ".js"]:
                 if (possible_path.with_suffix(ext)).is_file():
                    return possible_path.with_suffix(ext)
            if possible_path.is_dir():
                for ext in [".ets", ".ts", ".js"]:
                    if (possible_path / f"index{ext}").is_file():
                        return possible_path / f"index{ext}"
        return None