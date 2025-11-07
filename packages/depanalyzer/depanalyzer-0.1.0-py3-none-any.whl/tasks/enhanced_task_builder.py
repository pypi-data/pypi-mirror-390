#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强的任务构建器，支持第三方库依赖管理和动态任务生成
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Callable, Any

from tasks.task_system import Task, TaskScheduler, TaskType
from base.registry import ParserPair
from tasks.parse_types import ParseTask
from dependencies.dependency_manager import (
    DependencyManager, DependencyFetcher, DependencySpec, DependencyResult
)
from utils.graph import GraphManager

logger = logging.getLogger("depanalyzer.enhanced_task_builder")


class EnhancedTaskBuilder:
    """增强的任务构建器，支持第三方库依赖管理"""
    
    def __init__(self, repo_root: str, shared_graph: GraphManager, 
                 max_dependency_depth: int = 3):
        self.repo_root = repo_root
        self.shared_graph = shared_graph
        
        # 依赖管理
        self.dependency_manager = DependencyManager(
            cache_root=f"{repo_root}/.depanalyzer_cache",
            max_depth=max_dependency_depth
        )
        self.dependency_fetcher = DependencyFetcher(self.dependency_manager)
        
        # 跟踪已处理的依赖深度层级
        self.current_depth = 0
        self.max_depth = max_dependency_depth
        
        logger.info(f"Enhanced task builder initialized with max dependency depth: {max_dependency_depth}")
        
    def build_tasks(self, parsers: Dict[str, ParserPair]) -> TaskScheduler:
        """构建所有任务，包括依赖管理任务"""
        scheduler = TaskScheduler()
        
        # 收集所有解析器的文件信息
        parse_tasks = self._collect_parse_tasks(parsers)
        
        # 构建本地解析任务（带依赖检测）
        code_task_ids = self._build_enhanced_code_parse_tasks(scheduler, parsers, parse_tasks)
        config_task_ids = self._build_config_parse_tasks(scheduler, parsers, parse_tasks, code_task_ids)
        
        # 构建依赖检测任务（在本地解析完成后执行）
        dependency_check_task_ids = self._build_dependency_check_tasks(
            scheduler, parsers, parse_tasks, code_task_ids | config_task_ids
        )
        
        # 后处理任务需要等待所有解析任务完成（包括后续动态生成的依赖解析任务）
        # 这里先创建占位符，实际依赖会在运行时动态调整
        post_process_task_ids = self._build_post_process_tasks(
            scheduler, parsers, code_task_ids | config_task_ids | dependency_check_task_ids
        )
        
        # 验证依赖关系
        if not scheduler.validate_dependencies():
            raise ValueError("Task dependency graph contains cycles")
            
        logger.info(f"Built {len(scheduler.tasks)} initial tasks")
        return scheduler
        
    def _build_enhanced_code_parse_tasks(self, scheduler: TaskScheduler, 
                                        parsers: Dict[str, ParserPair],
                                        parse_tasks: Dict[str, ParseTask]) -> Set[str]:
        """构建增强的代码解析任务（支持依赖检测）"""
        task_ids = set()
        
        for name, pair in parsers.items():
            parse_task = parse_tasks[name]
            
            if not parse_task.code_files:
                continue
                
            task_id = f"code_parse_{name}"
            
            def create_enhanced_code_parse_func(parser_pair, ptask, parser_name):
                def enhanced_code_parse_func():
                    parser = parser_pair.code(ptask.repo_root, self.shared_graph)
                    parser.parse_files(ptask.code_files, self.shared_graph)
                    
                    # 解析完成后，发现依赖但不立即处理
                    # 依赖检测将由专门的任务处理
                    return f"Parsed {len(ptask.code_files)} code files for {parser_name}"
                return enhanced_code_parse_func
            
            task = Task(
                task_id=task_id,
                task_type=TaskType.CODE_PARSE,
                parser_name=name,
                func=create_enhanced_code_parse_func(pair, parse_task, name),
                dependencies=set()
            )
            
            scheduler.add_task(task)
            task_ids.add(task_id)
            
        return task_ids
        
    def _build_dependency_check_tasks(self, scheduler: TaskScheduler,
                                     parsers: Dict[str, ParserPair],
                                     parse_tasks: Dict[str, ParseTask],
                                     local_parse_task_ids: Set[str]) -> Set[str]:
        """构建依赖检测任务，在本地解析完成后检测第三方库依赖"""
        task_ids = set()
        
        for name, pair in parsers.items():
            parse_task = parse_tasks[name]
            
            if not parse_task.code_files and not parse_task.config_files:
                continue
                
            task_id = f"dependency_check_{name}"
            
            def create_dependency_check_func(parser_pair, ptask, parser_name, task_scheduler):
                def dependency_check_func():
                    parser = parser_pair.code(ptask.repo_root, self.shared_graph)
                    
                    # 发现代码文件中的依赖
                    discovered_deps = []
                    if ptask.code_files:
                        discovered_deps.extend(parser.discover_dependencies(ptask.code_files))
                    
                    # 发现配置文件中的依赖
                    if ptask.config_files and parser_pair.config:
                        config_parser = parser_pair.config(ptask.repo_root, self.shared_graph)
                        discovered_deps.extend(config_parser.discover_dependencies(ptask.config_files))
                    
                    logger.info(f"Discovered {len(discovered_deps)} dependencies for {parser_name}")
                    
                    # 过滤需要拉取的依赖
                    deps_to_fetch = [dep for dep in discovered_deps if self.dependency_manager.should_fetch(dep)]
                    
                    if deps_to_fetch:
                        # 动态创建依赖拉取和解析任务
                        new_tasks = self._create_dependency_tasks(deps_to_fetch, parser_name)
                        
                        # 动态添加到调度器
                        task_scheduler.add_dynamic_tasks(new_tasks)
                        
                        logger.info(f"Created {len(new_tasks)} dependency tasks for {parser_name}")
                    
                    return f"Checked dependencies for {parser_name}: {len(deps_to_fetch)} to fetch"
                return dependency_check_func
            
            task = Task(
                task_id=task_id,
                task_type=TaskType.CODE_PARSE,  # 使用CODE_PARSE类型以确保优先级正确
                parser_name=name,
                func=create_dependency_check_func(pair, parse_task, name, scheduler),
                dependencies=local_parse_task_ids  # 依赖所有本地解析任务
            )
            
            scheduler.add_task(task)
            task_ids.add(task_id)
            
        return task_ids
        
    def _create_dependency_tasks(self, dependencies: List[DependencySpec], 
                               parent_parser: str) -> List[Task]:
        """为给定的依赖列表创建拉取和解析任务"""
        tasks = []
        
        for dep in dependencies:
            # 标记为待处理
            self.dependency_manager.mark_pending(dep)
            
            # 创建拉取任务
            fetch_task_id = f"fetch_{dep.dependency_type.name.lower()}_{dep.name}_{dep.version}"
            
            def create_fetch_func(dep_spec):
                def fetch_func():
                    result = self.dependency_fetcher.fetch(dep_spec)
                    self.dependency_manager.mark_completed(result)
                    
                    if result.success and result.discovered_deps:
                        logger.info(f"Dependency {dep_spec.name} discovered {len(result.discovered_deps)} new dependencies")
                        # 注意：这里不立即创建新任务，而是记录发现的依赖
                        # 新依赖将在后续的递归检查中处理
                    
                    return f"Fetched {dep_spec.name}@{dep_spec.version}"
                return fetch_func
            
            fetch_task = Task(
                task_id=fetch_task_id,
                task_type=TaskType.DEPENDENCY_FETCH,
                parser_name=parent_parser,
                func=create_fetch_func(dep),
                dependencies=set()  # 拉取任务无依赖，可以立即执行
            )
            
            tasks.append(fetch_task)
            
            # 创建解析任务（依赖拉取任务）
            parse_task_id = f"parse_{dep.dependency_type.name.lower()}_{dep.name}_{dep.version}"
            
            def create_parse_func(dep_spec):
                def parse_func():
                    # 获取拉取结果
                    fetched_deps = self.dependency_manager.get_fetched_dependencies()
                    target_dep = None
                    
                    for fetched in fetched_deps:
                        if fetched.spec.unique_key == dep_spec.unique_key:
                            target_dep = fetched
                            break
                    
                    if target_dep and target_dep.local_path:
                        # TODO: 这里需要根据依赖类型选择合适的解析器
                        # 暂时跳过实际解析，只记录
                        logger.info(f"Would parse dependency {dep_spec.name} at {target_dep.local_path}")
                        return f"Parsed dependency {dep_spec.name}"
                    else:
                        raise Exception(f"Dependency {dep_spec.name} not found or failed to fetch")
                        
                return parse_func
            
            parse_task = Task(
                task_id=parse_task_id,
                task_type=TaskType.DEPENDENCY_PARSE,
                parser_name=parent_parser,
                func=create_parse_func(dep),
                dependencies={fetch_task_id}  # 依赖对应的拉取任务
            )
            
            tasks.append(parse_task)
            
        return tasks
        
    # === 从原TaskBuilder合并的基础方法 ===
    
    def _collect_parse_tasks(self, parsers: Dict[str, ParserPair]) -> Dict[str, ParseTask]:
        """收集所有解析器的解析任务信息"""
        parse_tasks = {}
        
        for name, pair in parsers.items():
            code_files = pair.code.discover_code_files(self.repo_root)
            config_files = pair.config.discover_config_files(self.repo_root) if pair.config else []
            
            logger.info(f"Parser [{name}]: discovered {len(code_files)} code files, {len(config_files)} config files")
            
            parse_tasks[name] = ParseTask(
                repo_root=self.repo_root,
                parser_name=name,
                code_files=code_files,
                config_files=config_files
            )
            
        return parse_tasks
        
    def _build_config_parse_tasks(self, scheduler: TaskScheduler,
                                 parsers: Dict[str, ParserPair],
                                 parse_tasks: Dict[str, ParseTask],
                                 code_task_ids: Set[str]) -> Set[str]:
        """构建配置解析任务（依赖对应的代码解析任务）"""
        task_ids = set()
        
        for name, pair in parsers.items():
            if not pair.config:
                logger.debug(f"Skipping config parsing for {name} - no config parser")
                continue
                
            parse_task = parse_tasks[name]
            
            if not parse_task.config_files:
                logger.debug(f"Skipping config parsing for {name} - no files found")
                continue
                
            task_id = f"config_parse_{name}"
            code_task_id = f"code_parse_{name}"
            
            # 配置解析依赖对应的代码解析任务（如果存在）
            dependencies = {code_task_id} if code_task_id in code_task_ids else set()
            
            def create_config_parse_func(parser_pair, ptask):
                def config_parse_func():
                    parser = parser_pair.config(ptask.repo_root, self.shared_graph)
                    parser.parse_files(ptask.config_files, self.shared_graph)
                    return f"Parsed {len(ptask.config_files)} config files"
                return config_parse_func
            
            task = Task(
                task_id=task_id,
                task_type=TaskType.CONFIG_PARSE,
                parser_name=name,
                func=create_config_parse_func(pair, parse_task),
                dependencies=dependencies
            )
            
            scheduler.add_task(task)
            task_ids.add(task_id)
            logger.debug(f"Created config parsing task: {task_id} with dependencies: {dependencies}")
            
        return task_ids
        
    def _build_post_process_tasks(self, scheduler: TaskScheduler,
                                 parsers: Dict[str, ParserPair],
                                 all_parse_task_ids: Set[str]) -> Set[str]:
        """构建后处理任务（依赖所有解析任务）"""
        task_ids = set()
        
        for name, pair in parsers.items():
            if not pair.config:
                logger.debug(f"Skipping post-processing for {name} - no config parser")
                continue
                
            task_id = f"post_process_{name}"
            
            def create_post_process_func(parser_pair, parser_name):
                def post_process_func():
                    parser = parser_pair.config(self.repo_root, self.shared_graph)
                    parser.post_process(self.shared_graph)
                    return f"Post-processed dependencies for {parser_name}"
                return post_process_func
            
            task = Task(
                task_id=task_id,
                task_type=TaskType.POST_PROCESS,
                parser_name=name,
                func=create_post_process_func(pair, name),
                dependencies=all_parse_task_ids.copy()  # 后处理依赖所有解析任务
            )
            
            scheduler.add_task(task)
            task_ids.add(task_id)
            logger.debug(f"Created post-processing task: {task_id} with {len(all_parse_task_ids)} dependencies")
            
        return task_ids
