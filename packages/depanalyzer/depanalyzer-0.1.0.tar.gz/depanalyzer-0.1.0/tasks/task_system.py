
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级任务队列系统，支持任务依赖关系和并行执行
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict, deque

logger = logging.getLogger("depanalyzer.task_system")


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = auto()      # 等待执行
    READY = auto()        # 依赖已满足，可以执行
    RUNNING = auto()      # 正在执行
    COMPLETED = auto()    # 已完成
    FAILED = auto()       # 执行失败


class TaskType(Enum):
    """任务类型枚举"""
    CODE_PARSE = auto()       # 代码解析任务
    CONFIG_PARSE = auto()     # 配置解析任务
    DEPENDENCY_FETCH = auto() # 第三方库拉取任务  
    DEPENDENCY_PARSE = auto() # 第三方库解析任务
    POST_PROCESS = auto()     # 后处理任务


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0


@dataclass
class Task:
    """任务定义"""
    task_id: str
    task_type: TaskType
    parser_name: str
    func: Callable[[], Any]
    dependencies: Set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    priority: int = 0  # 优先级，数字越小优先级越高
    
    def __post_init__(self):
        """后初始化，设置任务优先级"""
        if self.task_type == TaskType.CODE_PARSE:
            self.priority = 1
        elif self.task_type == TaskType.CONFIG_PARSE:
            self.priority = 2
        elif self.task_type == TaskType.DEPENDENCY_FETCH:
            self.priority = 3
        elif self.task_type == TaskType.DEPENDENCY_PARSE:
            self.priority = 4
        elif self.task_type == TaskType.POST_PROCESS:
            self.priority = 5


class TaskScheduler:
    """任务调度器，支持依赖关系管理和并行执行"""
    
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_deps: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.RLock()
        self._completed_tasks: Set[str] = set()
        self._running_tasks: Set[str] = set()
        
    def add_task(self, task: Task) -> None:
        """添加任务到调度器"""
        with self.lock:
            self.tasks[task.task_id] = task
            self.dependency_graph[task.task_id] = task.dependencies.copy()
            
            # 构建反向依赖图
            for dep in task.dependencies:
                self.reverse_deps[dep].add(task.task_id)
                
        logger.debug(f"Added task {task.task_id} with dependencies: {task.dependencies}")
        
    def add_dynamic_tasks(self, tasks: List[Task]) -> None:
        """动态添加任务（在运行过程中）"""
        with self.lock:
            for task in tasks:
                if task.task_id not in self.tasks:
                    self.add_task(task)
                    logger.info(f"Dynamically added task: {task.task_id}")
        
    def _get_ready_tasks(self) -> List[Task]:
        """获取所有可以执行的任务（依赖已满足）"""
        ready_tasks = []
        
        with self.lock:
            for task_id, task in self.tasks.items():
                if (task.status == TaskStatus.PENDING and 
                    all(dep in self._completed_tasks for dep in task.dependencies)):
                    task.status = TaskStatus.READY
                    ready_tasks.append(task)
                    
        # 按优先级排序
        ready_tasks.sort(key=lambda t: t.priority)
        return ready_tasks
        
    def _mark_task_completed(self, task_id: str, result: TaskResult) -> None:
        """标记任务为已完成"""
        with self.lock:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            task.result = result
            
            if result.success:
                self._completed_tasks.add(task_id)
                logger.info(f"Task {task_id} completed successfully in {result.execution_time:.2f}s")
            else:
                logger.error(f"Task {task_id} failed: {result.error}")
                
            self._running_tasks.discard(task_id)
            
    def _execute_task(self, task: Task) -> TaskResult:
        """执行单个任务"""
        start_time = time.time()
        
        try:
            with self.lock:
                task.status = TaskStatus.RUNNING
                self._running_tasks.add(task.task_id)
                
            logger.info(f"Starting task {task.task_id} ({task.task_type.name})")
            result = task.func()
            
            execution_time = time.time() - start_time
            return TaskResult(success=True, result=result, execution_time=execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Task {task.task_id} failed with error: {e}")
            return TaskResult(success=False, error=e, execution_time=execution_time)
            
    def run_all(self) -> Dict[str, TaskResult]:
        """执行所有任务，支持并行处理和依赖关系"""
        logger.info(f"Starting task execution with {self.max_workers} workers")
        logger.info(f"Total tasks: {len(self.tasks)}")
        
        start_time = time.time()
        results: Dict[str, TaskResult] = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures: Dict[Future, str] = {}
            
            while len(self._completed_tasks) + len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]) < len(self.tasks):
                # 获取可执行的任务
                ready_tasks = self._get_ready_tasks()
                
                # 提交新任务
                for task in ready_tasks:
                    if len(futures) < self.max_workers:
                        future = executor.submit(self._execute_task, task)
                        futures[future] = task.task_id
                        logger.debug(f"Submitted task {task.task_id} for execution")
                
                # 等待任务完成
                if futures:
                    # 修复超时问题：使用更长的超时时间，或者处理完成的任务
                    try:
                        completed_futures = []
                        for future in as_completed(futures.keys(), timeout=5.0):  # 增加超时时间到5秒
                            completed_futures.append(future)
                            
                        for future in completed_futures:
                            task_id = futures.pop(future)
                            result = future.result()
                            self._mark_task_completed(task_id, result)
                            results[task_id] = result
                    except Exception as e:
                        # 处理超时或其他异常
                        logger.warning(f"Exception in task execution loop: {e}")
                        # 检查是否有已完成的futures
                        completed_futures = [f for f in futures.keys() if f.done()]
                        for future in completed_futures:
                            task_id = futures.pop(future)
                            try:
                                result = future.result()
                                self._mark_task_completed(task_id, result)
                                results[task_id] = result
                            except Exception as task_error:
                                logger.error(f"Task {task_id} failed: {task_error}")
                                error_result = TaskResult(success=False, error=task_error, execution_time=0.0)
                                self._mark_task_completed(task_id, error_result)
                                results[task_id] = error_result
                else:
                    # 没有任务在执行，检查是否有死锁
                    if not self._get_ready_tasks():
                        logger.warning("No ready tasks and no running tasks - possible dependency cycle")
                        break
                        
                # 短暂休眠避免CPU空转
                time.sleep(0.01)
                
        elapsed = time.time() - start_time
        successful_tasks = len([r for r in results.values() if r.success])
        failed_tasks = len(results) - successful_tasks
        
        logger.info(f"All tasks completed in {elapsed:.2f}s")
        logger.info(f"Successful: {successful_tasks}, Failed: {failed_tasks}")
        
        return results
        
    def get_task_status(self) -> Dict[str, TaskStatus]:
        """获取所有任务的状态"""
        with self.lock:
            return {task_id: task.status for task_id, task in self.tasks.items()}
            
    def validate_dependencies(self) -> bool:
        """验证依赖关系是否有循环依赖"""
        # 使用拓扑排序检测循环依赖
        in_degree = defaultdict(int)
        
        # 计算入度
        for task_id in self.tasks:
            in_degree[task_id] = len(self.dependency_graph[task_id])
            
        # 拓扑排序
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        visited_count = 0
        
        while queue:
            current = queue.popleft()
            visited_count += 1
            
            # 减少依赖当前节点的所有节点的入度
            for dependent in self.reverse_deps[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
                    
        # 如果访问的节点数等于总节点数，则无循环依赖
        has_cycle = visited_count != len(self.tasks)
        if has_cycle:
            logger.error("Detected dependency cycle in task graph!")
            
        return not has_cycle
