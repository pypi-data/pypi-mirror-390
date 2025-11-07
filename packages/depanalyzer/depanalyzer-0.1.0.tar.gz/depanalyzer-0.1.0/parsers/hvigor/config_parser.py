import json5
from pathlib import Path
from typing import List, Dict, Any

from base.base import BaseConfigParser
from utils.graph import GraphManager, Vertex, Edge

class ConfigParser(BaseConfigParser):
    """
    Parses all critical configuration files for ArkTS/HVigor projects, creating
    all nodes and edges with a unified format. It fully retains all original

    functionality while adding a generic linking mechanism to bridge ArkTS modules
    with their native C/C++ implementations.
    """
    NAME = "hvigor"
    CONFIG_GLOBS = ["**/build-profile.json5", "**/oh-package.json5", "**/module.json5", "**/oh-package-lock.json5"]

    def parse_file(self, file_path: Path, shared_graph: GraphManager) -> None:
        """Parses a single configuration file and updates the graph and context."""
        build_context = shared_graph.graph.graph.get('build_context', {})
        parsed_data = self._parse_single_config(file_path)
        self._process_config_result(parsed_data, shared_graph, build_context)

    def parse_files(self, files: List[Path], graph: GraphManager) -> None:
        """Orchestrates the parsing process and all final linking passes."""
        with self.graph_lock:
            if 'build_context' not in graph.graph.graph:
                graph.graph.graph['build_context'] = {
                    "module_paths": {},
                    "project_dependencies": [],
                    "external_libraries": {},
                    "native_bridges": {} # Maps native lib name to its .d.ts bridge ID
                }

        super().parse_files(files, graph)

        build_context = graph.graph.graph.get('build_context', {})
        with self.graph_lock:
            all_nodes = list(graph.nodes(data=True))
            module_paths = build_context.get("module_paths", {})
            
            # Linking Pass A: Connect ArkTS code nodes to their parent modules
            if module_paths:
                for node_id, node_data in all_nodes:
                    if node_data.get("type") == "code" and node_data.get("parser_name") == self.NAME:
                        for module_root_rel, module_name in module_paths.items():
                            if node_id.replace('\\', '/').startswith(module_root_rel.replace('\\', '/')):
                                module_id_graph = f"module:{module_name}"
                                if graph.get_node_data(module_id_graph):
                                    graph.add_edge(Edge(u=module_id_graph, v=node_id, type="contains", parser_name=self.NAME))
                                break

            # Linking Pass B: Connect modules to external libraries
            project_deps = build_context.get("project_dependencies", [])
            external_libs = build_context.get("external_libraries", {})
            for module_name in module_paths.values():
                module_id = f"module:{module_name}"
                for dep_name in project_deps:
                    if dep_name in external_libs:
                        lib_info = external_libs[dep_name]
                        lib_version = lib_info.get("version")
                        lib_id = f"ext_lib:{dep_name}@{lib_version}" if lib_version else f"ext_lib:{dep_name}"
                        if graph.get_node_data(module_id) and graph.get_node_data(lib_id):
                            graph.add_edge(Edge(u=module_id, v=lib_id, type="depends_on", parser_name=self.NAME))
            
            # Linking Pass C (Native Bridge): Connect .d.ts to C/C++ source files
            # （预留）连接原生实现: 根据 build_context 中记录的桥梁信息，预留出建立 implements_native 关系的能力，等待 CMAKE 解析器提供 C/C++ 文件节点后即可自动连接。
            native_bridges = build_context.get("native_bridges", {})
            # Assume a C/CMAKE parser populates this context structure
            c_context = graph.graph.graph.get("c_context", {}).get("targets", {})

            for lib_name, bridge_info in native_bridges.items():
                bridge_dts_id = bridge_info.get("dts_id")
                if not bridge_dts_id or not graph.get_node_data(bridge_dts_id):
                    continue
                
                target_name = lib_name.replace("lib", "").split('.')[0]
                c_source_ids = c_context.get(target_name, [])
                
                for c_id in c_source_ids:
                    if graph.get_node_data(c_id):
                        graph.add_edge(Edge(u=bridge_dts_id, v=c_id, type="implements_native", parser_name="c"))

    def post_process(self, shared_graph: GraphManager) -> None:
        """
        后处理钩子：将指向 .d.ts 的依赖关系重定向到真正的动态库。
        
        这个方法在所有解析器完成后调用，确保 C++ 动态库节点已经被创建。
        """
        build_context = shared_graph.graph.graph.get('build_context', {})
        native_bridges = build_context.get("native_bridges", {})
        
        if not native_bridges:
            return
        
        with self.graph_lock:
            # 为每个 native bridge 找到对应的 C++ 动态库并重定向依赖
            for lib_name, bridge_info in native_bridges.items():
                dts_id = bridge_info.get("dts_id")
                if not dts_id or not shared_graph.get_node_data(dts_id):
                    continue
                
                # 查找对应的 C++ 动态库节点
                cpp_library_id = self._find_cpp_library_by_name(shared_graph, lib_name)
                if not cpp_library_id:
                    continue
                
                # 查找所有指向 .d.ts 的边并重定向到动态库
                edges_to_redirect = []
                for u, v, key, data in shared_graph.edges(data=True, keys=True):
                    if v == dts_id:
                        edges_to_redirect.append((u, v, key, data))
                
                # 执行重定向
                for u, v, key, data in edges_to_redirect:
                    # 删除原来指向 .d.ts 的边
                    shared_graph.remove_edge((u, v, key))
                    
                    # 创建指向 C++ 动态库的新边
                    new_edge = Edge(u=u, v=cpp_library_id, **data)
                    shared_graph.add_edge(new_edge)
                    
                    print(f"[HVigor Post-Process] Redirected dependency: {u} -> {dts_id} => {u} -> {cpp_library_id}")

    def _find_cpp_library_by_name(self, shared_graph: GraphManager, lib_name: str) -> str:
        """
        根据库名查找对应的 C++ 动态库节点ID。
        
        Args:
            shared_graph: 共享图
            lib_name: 库名，如 "libdimina.so" 或 "libentry.so"
        
        Returns:
            对应的 C++ 动态库节点ID，如找不到返回空字符串
        """
        # 从库名提取目标名称：@types/libentry.so -> entry, @didi-dimina/dimina -> dimina, libdimina.so -> dimina
        # 处理 @xxx/ 前缀的情况
        if lib_name.startswith("@"):
            # 找到第一个 '/' 后面的部分
            slash_index = lib_name.find("/")
            if slash_index != -1:
                clean_name = lib_name[slash_index + 1:]  # 移除 "@xxx/" 前缀
            else:
                clean_name = lib_name  # 如果没有 '/'，保持原样
        else:
            clean_name = lib_name
        
        # libentry.so -> entry, libdimina.so -> dimina
        if clean_name.startswith("lib"):
            target_name = clean_name[3:]  # 移除 "lib" 前缀
        else:
            target_name = clean_name
        
        # 移除 .so 后缀
        if target_name.endswith(".so"):
            target_name = target_name[:-3]
        
        # 查找类型为 shared_library 且目标名匹配的节点
        for node_id, node_data in shared_graph.nodes(data=True):
            if (node_data.get("type") == "shared_library" and 
                node_data.get("parser_name") == "cmake" and
                node_id.endswith(f":{target_name}")):
                return node_id
        
        return ""

    def _parse_single_config(self, file_path: Path) -> Dict[str, Any]:
        """Parses a single JSON5 config, handling all known file types."""
        result = {"file": file_path, "type": "unknown"}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json5.load(f)

            if file_path.name == "build-profile.json5":
                result["type"] = "build_profile"
                result["modules"] = config.get("modules", [])
            elif file_path.name == "oh-package.json5":
                result["type"] = "package_dependencies"
                
                # FIX: Check both dependencies and devDependencies for native libs
                all_deps = {**config.get("dependencies", {}), **config.get("devDependencies", {})}
                result["dependencies"] = list(all_deps.keys())
                
                native_deps = {name: path.replace("file:", "", 1) for name, path in all_deps.items() if isinstance(path, str) and path.startswith("file:")}
                if native_deps:
                    result["native_dependencies"] = native_deps
                if "types" in config:
                    result["bridge_dts"] = config.get("types")

            elif file_path.name == "module.json5":
                result["type"] = "module_config"
                result["module_name"] = config.get("module", {}).get("name", file_path.parent.name)
            elif file_path.name == "oh-package-lock.json5":
                result["type"] = "lock_file"
                result["external_dependencies"] = [{"name": name, "version": info.get("version")} for name, info in config.get("dependencies", {}).items()]
        except Exception as e:
            print(f"Warning: could not parse build config {file_path}: {e}")
        return result

    def _process_config_result(self, result: Dict[str, Any], graph: GraphManager, build_context: Dict[str, Any]):
        """Processes a single parsed config file, creating nodes and discovering bridges."""
        config_file: Path = result.get("file")
        if not config_file: return

        rel_path_str = str(config_file.relative_to(self.repo_root))
        
        with self.graph_lock:
            graph.add_node(Vertex(label=rel_path_str, id=rel_path_str, src_path=str(config_file.resolve()), type="config", name=config_file.name, parser_name=self.NAME))

            result_type = result.get("type")

            if result_type == "build_profile":
                for module_item in result.get("modules", []):
                    module_name = module_item.get("name") if isinstance(module_item, dict) else module_item
                    if not module_name or not isinstance(module_name, str): continue
                    
                    module_id = f"module:{module_name}"
                    module_root = Path(self.repo_root) / module_name
                    graph.add_node(Vertex(label=module_id, id=module_id, src_path=str(module_root.resolve()), type="module", name=module_name, parser_name=self.NAME))
                    graph.add_edge(Edge(u=module_id, v=rel_path_str, type="defined_by", parser_name=self.NAME))
                    
            elif result_type == "module_config":
                module_name = result.get("module_name")
                if not module_name: return
                
                module_id = f"module:{module_name}"
                module_root = config_file.parent.parent.parent
                graph.add_node(Vertex(label=module_id, id=module_id, src_path=str(module_root.resolve()), type="module", name=module_name, parser_name=self.NAME))
                graph.add_edge(Edge(u=module_id, v=rel_path_str, type="defined_by", parser_name=self.NAME))
                
                build_context["module_paths"][str(module_root.relative_to(self.repo_root))] = module_name
            
            elif result_type == "package_dependencies":
                # Process regular dependencies
                deps = result.get("dependencies", [])
                build_context["project_dependencies"].extend(d for d in deps if d not in build_context["project_dependencies"])

                # Process native dependencies (Step 1 & 2 of the普适方案)
                native_deps = result.get("native_dependencies", {})
                for lib_name, rel_type_path in native_deps.items():
                    try:
                        type_dir = (config_file.parent / rel_type_path).resolve()
                        native_pkg_json_path = type_dir / "oh-package.json5"
                        if native_pkg_json_path.exists():
                            with open(native_pkg_json_path, 'r', encoding='utf-8') as f:
                                native_pkg_config = json5.load(f)
                            dts_rel_path = native_pkg_config.get("types")
                            if dts_rel_path:
                                dts_abs_path = (native_pkg_json_path.parent / dts_rel_path).resolve()
                                dts_id = str(dts_abs_path.relative_to(self.repo_root))
                                build_context["native_bridges"][lib_name] = {"dts_id": dts_id}
                                graph.add_node(Vertex(label=dts_id, id=dts_id, src_path=str(dts_abs_path), type="code", name=Path(dts_id).name, parser_name=self.NAME))
                    except Exception as e:
                        print(f"Warning: could not process native dependency bridge for {lib_name}: {e}")

            elif result_type == "lock_file":
                for dep in result.get("external_dependencies", []):
                    lib_name = dep.get("name")
                    if lib_name:
                        build_context["external_libraries"][lib_name] = dep
                        lib_version = dep.get("version")
                        lib_id = f"ext_lib:{lib_name}@{lib_version}" if lib_version else f"ext_lib:{lib_name}"
                        graph.add_node(Vertex(label=lib_id, id=lib_id, src_path="N/A", type="external_library", name=lib_name, version=lib_version, parser_name=self.NAME))