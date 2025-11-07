
#!/usr/bin/env python3
import argparse
import json
import os
import traceback
from pathlib import Path
from core.orchestrator import Orchestrator
from utils.structure import DualLicenseEncoder
"""入口：依赖外部 pip 安装的 liscopelens。"""
LISCOPELENS_AVAILABLE = False
try:
    # 使用 pip 安装的 liscopelens 包
    import liscopelens  # type: ignore
    from liscopelens.api.scancode import detect_license  # type: ignore
    from liscopelens.api.base import check_compatibility  # type: ignore
    LISCOPELENS_AVAILABLE = True
    try:
        print(f"[depanalyzer] liscopelens loaded from: {getattr(liscopelens, '__file__', 'unknown')}")
    except Exception:
        pass
except Exception as e:
    print(f"[错误] liscopelens 模块导入失败: {e}")
    print("[错误] 许可证检测与兼容性检查需要先安装 liscopelens：pip install liscopelens")
    # 保持 False，由调用逻辑在启用 license-check 时终止

def main():
    ap = argparse.ArgumentParser(description="License Compatibility Detection Tool")
    ap.add_argument("--repo", required=True, help="Repository root to analyze")
    ap.add_argument("--out", required=True, help="Output graph file (.json or .gml)")
    ap.add_argument("--workers", type=int, default=8, help="Max parallel workers")
    ap.add_argument("--max-depth", type=int, default=3, 
                   help="Maximum recursion depth for third-party dependencies (default: 3)")
    
    # 新增许可证相关参数
    ap.add_argument("--enable-license-check", action="store_true", default=False,
                   help="Enable license detection and compatibility checking")
    ap.add_argument("--scancode-cmd", default="scancode", 
                   help="ScanCode executable name or path (default: scancode)")
    ap.add_argument("--license-out", 
                   help="Output file for final compatibility analysis result (default: add _compatible suffix to --out)")
    # 兼容旧参数 --shadow（等价于 --file-shadow）
    ap.add_argument("--shadow", help="[DEPRECATED] Equal to --file-shadow")
    # 新参数：文件级 shadow 与许可 shadow
    ap.add_argument("--file-shadow", dest="file_shadow", help="File shadow JSON path")
    ap.add_argument("--license-shadow", dest="license_shadow", help="License shadow JSON path")
    ap.add_argument("--license-map-out",
                   help="Output JSON file for the raw ScanCode license map (default: add _license_map suffix to --out)")
    
    args = ap.parse_args()

    print(f"[depanalyzer] Starting analysis")
    print(f"[depanalyzer] Repository: {args.repo}")
    print(f"[depanalyzer] Workers: {args.workers}")
    print(f"[depanalyzer] Max dependency depth: {args.max_depth}")
    
    if args.enable_license_check:
        print(f"[depanalyzer] License detection enabled")
        if not LISCOPELENS_AVAILABLE:
            print("[错误] 启用了许可证检查，但 liscopelens 模块不可用（导入失败）")
            return 1

    # 第一步：依赖分析
    print("\n=== 第一步：依赖关系分析 ===")
    orch = Orchestrator(args.repo, max_workers=args.workers, max_dependency_depth=args.max_depth)
    dependency_graph = orch.run()
    out_path = Path(args.out)
    fmt = "gml" if out_path.suffix.lower() == ".gml" else "json"
    # 使用类型映射导出：system_header/project_header/code -> code；库类型保持
    dependency_graph.save_with_mapping(
        str(out_path),
        save_format=fmt,
        unify_edge_label="dep",
    )
    print(f"[depanalyzer] 依赖图已保存到: {out_path}")

    # 为兼容 liscopelens 的 GraphManager，若主输出为 GML，则同时导出一份 JSON（node_link 格式）供后续使用
    graph_input_for_compat = dependency_graph
    if fmt == "gml":
        json_graph_path = out_path.with_suffix('.json')
        try:
            dependency_graph.save_with_mapping(
                str(json_graph_path),
                save_format="json",
                unify_edge_label="dep",
            )
            print(f"[depanalyzer] 同步导出 JSON 图以供兼容性检查: {json_graph_path}")
        except Exception as e:
            print(f"[警告] 导出 JSON 图失败，将尝试直接使用 GML 进行兼容性检查: {e}")
    
    # 如果没有启用许可证检查，到此结束
    if not args.enable_license_check:
        print("[depanalyzer] 分析完成")
        return 0
        
    # 第二步：许可证检测
    print("\n=== 第二步：许可证检测 ===")
    try:
        print(f"[depanalyzer] 正在扫描 {args.repo} 的许可证信息...")
        # 临时忽略大型二进制中间产物，减少 .a/.so 扫描失败对整体产物的影响
        # 注意：加入深层通配，匹配任意层级与带版本后缀的 .so
        scancode_ignores = [
            "--ignore", "*.a",
            "--ignore", "**/*.a",
            "--ignore", "**/lib/*.a",
            "--ignore", "*.so",
            "--ignore", "*.so.*",
            "--ignore", "**/*.so",
            "--ignore", "**/*.so.*",
            "--ignore", "**/lib/*.so*",
        ]
        # scancode 在同时传入多个输入路径时要求输入必须为相对路径
        # 这里临时切换工作目录到目标仓库，传入 "." 以避免绝对路径引发的错误
        old_cwd = os.getcwd()
        try:
            os.chdir(args.repo)
            license_map_raw = detect_license(
                args.repo,
                scancode_cmd=args.scancode_cmd,
                extra_args=scancode_ignores,
            )
        finally:
            os.chdir(old_cwd)
        
        # 获取依赖图中的所有节点标签（文件路径）
        graph_labels = set()
        parser_names = set()  # 收集所有parser_name来判断是否为混编项目
        for node_id, data in dependency_graph.nodes(data=True):
            # 使用节点的label或node_id作为路径
            label = data.get('label', str(node_id))
            if label:
                graph_labels.add(label)
            # 收集parser_name
            parser_name = data.get('parser_name')
            if parser_name:
                parser_names.add(parser_name)
        
        # 判断是否为混编项目（有多种parser_name）
        is_mixed_project = len(parser_names) > 1
        print(f"[depanalyzer] 依赖图包含 {len(graph_labels)} 个节点")
        print(f"[depanalyzer] 检测到 {len(parser_names)} 种解析器: {parser_names}")
        print(f"[depanalyzer] 项目类型: {'混编项目' if is_mixed_project else '单一语言项目'}")
        print(f"[depanalyzer] Scancode 扫描到 {len(license_map_raw)} 个文件")
        
        # 定义文档类文件（通常包含项目级别的许可证）
        doc_file_patterns = [
            'readme', 'license', 'copying', 'notice', 'authors',
            'contributors', 'copyright', 'patents', '.json', 
            'package.json', 'bower.json', '.podspec'
        ]
        
        def is_doc_file(file_path: str) -> bool:
            """判断是否为文档类文件"""
            file_path_lower = file_path.lower()
            return any(pattern in file_path_lower for pattern in doc_file_patterns)
        
        def get_directory_path(file_path: str) -> str:
            """获取文件所在目录的路径"""
            # 移除开头的 "//"
            path_without_prefix = file_path[2:] if file_path.startswith("//") else file_path
            # 获取目录路径
            dir_path = str(Path(path_without_prefix).parent)
            if dir_path == '.':
                return '//'
            return '//' + dir_path
        
        def find_nodes_in_directory(dir_path: str, node_types: list = None) -> list:
            """查找指定目录下指定类型的节点"""
            if node_types is None:
                node_types = ["code"]
            nodes = []
            for node_id, data in dependency_graph.nodes(data=True):
                label = data.get('label', str(node_id))
                if label and label.startswith(dir_path) and data.get('type') in node_types:
                    nodes.append((node_id, data))
            return nodes
        
        def find_intermediate_artifacts_in_directory(dir_path: str) -> list:
            """查找指定目录下的中间产物节点（编译目标）"""
            # 中间产物的类型
            artifact_types = [
                "shared_library",    # .so 共享库
                "static_library",    # .a 静态库  
                "executable",        # 可执行文件
                "module_library",    # 模块库
                "interface_library"  # 接口库
            ]
            return find_nodes_in_directory(dir_path, artifact_types)
        
        # 规范化路径并附加许可证
        license_map = {}
        repo_name = Path(args.repo).name  # 获取repo目录名（如 "source"）
        prefix_to_remove = f"//{repo_name}/"
        matched_count = 0
        doc_to_artifact_count = 0  # 文档许可证附加到中间产物的计数
        doc_to_root_count = 0  # 文档许可证附加到根节点的计数
        added_standalone_count = 0  # 独立添加的许可证文件节点计数
        
        for path, spdx in license_map_raw.items():
            # 规范化路径
            if path.startswith(prefix_to_remove):
                normalized_path = "//" + path[len(prefix_to_remove):]
            else:
                normalized_path = path
            
            license_map[normalized_path] = spdx
            
            # 如果文件已在依赖图中，直接附加许可证
            if normalized_path in graph_labels:
                node_data = dependency_graph.query_node_by_label(normalized_path)
                if node_data is not None:
                    node_data['license_spdx'] = spdx
                matched_count += 1
                continue
            
            # 文件不在依赖图中，需要判断如何处理
            is_doc = is_doc_file(normalized_path)
            
            if is_doc:
                # 文档类文件，需要附加到合适的节点
                dir_path = get_directory_path(normalized_path)
                
                if is_mixed_project:
                    # 混编项目：优先查找同目录下的中间产物（编译目标），其次才是代码节点
                    artifact_nodes = find_intermediate_artifacts_in_directory(dir_path)
                    
                    if artifact_nodes:
                        # 找到同目录的中间产物，附加许可证到这些中间产物
                        for node_id, node_data in artifact_nodes:
                            # 如果节点没有许可证或许可证为空，附加文档许可证
                            if not node_data.get('license_spdx'):
                                node_data['license_spdx'] = spdx
                                doc_to_artifact_count += 1
                    else:
                        # 同目录没有中间产物，附加到根节点
                        root_nodes = dependency_graph.root_nodes
                        for root_node in root_nodes:
                            root_data = dependency_graph.query_node_by_label(root_node)
                            if root_data and not root_data.get('license_spdx'):
                                root_data['license_spdx'] = spdx
                                doc_to_root_count += 1
                                break  # 只附加到第一个根节点
                else:
                    # 非混编项目：直接附加到根节点
                    root_nodes = dependency_graph.root_nodes
                    for root_node in root_nodes:
                        root_data = dependency_graph.query_node_by_label(root_node)
                        if root_data and not root_data.get('license_spdx'):
                            root_data['license_spdx'] = spdx
                            doc_to_root_count += 1
                            break  # 只附加到第一个根节点
            else:
                # 非文档类文件（例如代码文件但不在依赖图中），作为独立节点添加
                file_abs_path = Path(args.repo) / normalized_path[2:]  # 移除 "//"
                dependency_graph.graph.add_node(
                    normalized_path,
                    label=normalized_path,
                    src_path=str(file_abs_path),
                    type="license_file",
                    parser_name="scancode",
                    license_spdx=spdx
                )
                added_standalone_count += 1
        
        print(f"[depanalyzer] 已存在于依赖图的文件: {matched_count}")
        print(f"[depanalyzer] 文档许可证附加到同目录中间产物: {doc_to_artifact_count}")
        print(f"[depanalyzer] 文档许可证附加到根节点: {doc_to_root_count}")
        print(f"[depanalyzer] 新添加到依赖图的独立许可证文件: {added_standalone_count}")
        print(f"[depanalyzer] 最终依赖图节点数: {len(dependency_graph.nodes())}")
        
        # 重新保存依赖图（包含新添加的许可证文件节点）
        if added_standalone_count > 0 or doc_to_artifact_count > 0 or doc_to_root_count > 0:
            dependency_graph.save_with_mapping(
                str(out_path),
                save_format=fmt,
                unify_edge_label="dep",
            )
            print(f"[depanalyzer] 更新后的依赖图已保存到: {out_path}")

        # 保存原始 license_map 以便核对
        lm_out = Path(args.license_map_out) if args.license_map_out else out_path.with_stem(out_path.stem + "_license_map")
        with open(lm_out, "w", encoding="utf-8") as f:
            json.dump(license_map, f, ensure_ascii=False, indent=2)
        print(f"[depanalyzer] 许可证映射已保存到: {lm_out}")
    except Exception as e:
        print(f"[错误] 许可证检测失败: {e}")
        try:
            print(traceback.format_exc())
        except Exception:
            pass
        return 1
    
    # 第三步：兼容性检查
    print("\n=== 第三步：兼容性检查 ===")
    try:
        print(f"[depanalyzer] 正在进行许可证兼容性分析...")
        compatible_graph, _results = check_compatibility(
            license_map=license_map,
            graph_input=graph_input_for_compat,
            file_shadow=(args.file_shadow or args.shadow),
            license_shadow=(args.license_shadow if args.license_shadow else None),
            args="--ignore-unk"
        )
        
        # 保存兼容性检查结果（始终输出 JSON，避免 GML 对复杂属性的限制）
        if args.license_out:
            license_out_path = Path(args.license_out)
        else:
            # 默认添加 _compatible 后缀
            license_out_path = out_path.with_stem(out_path.stem + "_compatible")

        # 强制使用 JSON 格式，保证兼容性
        license_out_path = license_out_path.with_suffix(".json")
        compatible_graph.save(str(license_out_path), save_format="json")
        print(f"[depanalyzer] 兼容性分析结果已保存到: {license_out_path}")

        results_out_path = license_out_path.with_stem(license_out_path.stem + "_results").with_suffix(".json")
        try:
            os.makedirs(str(results_out_path.parent), exist_ok=True)
            with open(results_out_path, "w", encoding="utf-8") as rf:
                json.dump(_results, rf, ensure_ascii=False, indent=2, cls=DualLicenseEncoder)
            print(f"[depanalyzer] 兼容性检查详细结果已保存到: {results_out_path}")
        except Exception as re:
            print(f"[警告] 保存兼容性检查详细结果失败: {re}")
        
    except Exception as e:
        print(f"[错误] 兼容性检查失败: {e}")
        try:
            print(traceback.format_exc())
        except Exception:
            pass
        return 1
    
    print("\n[depanalyzer] 完整分析流程已完成！")
    return 0

if __name__ == "__main__":
    main()
