from typing import Dict
from base.registry import discover_parsers, ParserPair
from tasks.task_system import TaskScheduler, TaskResult
from tasks.enhanced_task_builder import EnhancedTaskBuilder
from dependencies.dependency_manager import DependencyManager
from utils.graph import GraphManager
import logging
import time

logger = logging.getLogger("depanalyzer.orchestrator")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)


class Orchestrator:
    """
    编排器，使用支持依赖关系和第三方库管理的任务调度系统
    """
    def __init__(self, repo_root: str, max_workers: int = 8, max_dependency_depth: int = 3) -> None:
        self.repo_root = repo_root
        self.max_workers = max_workers
        self.max_dependency_depth = max_dependency_depth
        self.parsers: Dict[str, ParserPair] = discover_parsers()
        # Create global shared graph
        self.shared_graph = GraphManager()
        # Enhanced task builder for creating tasks with dependency management
        self.task_builder = EnhancedTaskBuilder(repo_root, self.shared_graph, max_dependency_depth)

        logger.info("Discovered %d parsers:", len(self.parsers))
        for name, pair in self.parsers.items():
            logger.info("  - %s (code: %s, config: %s)",
                        name,
                        pair.code.__name__ if pair.code else "None",
                        pair.config.__name__ if pair.config else "None")
        
        logger.info(f"Max dependency depth: {max_dependency_depth}")
        logger.info(f"Dependency cache: {repo_root}/.depanalyzer_cache")


    def run(self) -> GraphManager:
        """
        使用新的任务调度系统执行依赖分析
        支持任务依赖关系管理、第三方库拉取和最优并行执行
        """
        start_time = time.time()
        logger.info("Starting dependency analysis on repo: %s", self.repo_root)
        logger.info("Using task-based architecture with third-party dependency management")

        # 构建任务调度器
        logger.info("Building task scheduler with %d max workers", self.max_workers)
        scheduler = self.task_builder.build_tasks(self.parsers)
        scheduler.max_workers = self.max_workers

        # 显示任务统计信息
        task_stats = self._get_task_statistics(scheduler)
        logger.info("Initial task breakdown: %s", task_stats)

        # 执行所有任务
        logger.info("Executing tasks with dependency-aware scheduling and dynamic task generation...")
        results = scheduler.run_all()

        # 分析执行结果
        self._analyze_results(results)
        
        # 显示依赖管理统计信息
        self._analyze_dependency_results()

        elapsed = time.time() - start_time
        logger.info("All tasks completed in %.2fs", elapsed)
        logger.info("Global graph contains %d nodes and %d edges", 
                   len(self.shared_graph.nodes()), len(self.shared_graph.edges()))

        return self.shared_graph

    def _get_task_statistics(self, scheduler: TaskScheduler) -> Dict[str, int]:
        """获取任务统计信息"""
        stats = {
            "code_parse": 0, 
            "config_parse": 0, 
            "dependency_fetch": 0,
            "dependency_parse": 0,
            "post_process": 0
        }
        
        for task in scheduler.tasks.values():
            task_type = task.task_type.name.lower()
            if task_type.startswith("code"):
                stats["code_parse"] += 1
            elif task_type.startswith("config"):
                stats["config_parse"] += 1
            elif "dependency_fetch" in task_type:
                stats["dependency_fetch"] += 1
            elif "dependency_parse" in task_type:
                stats["dependency_parse"] += 1
            elif task_type.startswith("post"):
                stats["post_process"] += 1
                
        return stats
        
    def _analyze_results(self, results: Dict[str, TaskResult]) -> None:
        """分析任务执行结果"""
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        
        if failed > 0:
            logger.warning(f"Task execution completed with {failed} failures")
            
            # 显示失败的任务
            for task_id, result in results.items():
                if not result.success:
                    logger.error(f"Failed task {task_id}: {result.error}")
        else:
            logger.info("All tasks completed successfully!")
            
        # 显示执行时间统计
        execution_times = [r.execution_time for r in results.values() if r.success]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            logger.info(f"Execution time stats - Avg: {avg_time:.2f}s, Max: {max_time:.2f}s, Min: {min_time:.2f}s")
            
    def _analyze_dependency_results(self) -> None:
        """分析依赖管理结果"""
        dep_manager = self.task_builder.dependency_manager
        
        # 获取依赖管理统计
        status = dep_manager.get_status()
        logger.info("Dependency management summary:")
        logger.info(f"  - Fetched dependencies: {status['fetched']}")
        logger.info(f"  - Failed dependencies: {status['failed']}")
        logger.info(f"  - Total processed: {status['total_processed']}")
        
        # 显示成功拉取的依赖
        fetched_deps = dep_manager.get_fetched_dependencies()
        if fetched_deps:
            logger.info("Successfully fetched dependencies:")
            for dep_result in fetched_deps[:10]:  # 只显示前10个
                logger.info(f"  - {dep_result.spec.name}@{dep_result.spec.version} "
                          f"({dep_result.spec.dependency_type.name}) -> {dep_result.local_path}")
            
            if len(fetched_deps) > 10:
                logger.info(f"  ... and {len(fetched_deps) - 10} more dependencies")
                
        # 显示发现的递归依赖
        all_discovered = dep_manager.get_all_discovered_dependencies()
        if all_discovered:
            logger.info(f"Discovered {len(all_discovered)} additional dependencies through recursion")
            
            # 按深度分组显示
            depth_stats = {}
            for dep in all_discovered:
                depth_stats[dep.depth] = depth_stats.get(dep.depth, 0) + 1
                
            if depth_stats:
                logger.info("Dependencies by depth:")
                for depth, count in sorted(depth_stats.items()):
                    logger.info(f"  - Depth {depth}: {count} dependencies")
