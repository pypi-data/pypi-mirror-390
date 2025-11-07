#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
第三方库依赖管理系统
"""

import hashlib
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
from enum import Enum, auto


logger = logging.getLogger("depanalyzer.dependency_manager")


class DependencyType(Enum):
    """依赖类型枚举"""
    NPM = auto()           # npm包
    MAVEN = auto()         # Maven依赖
    PIP = auto()           # Python包
    GIT = auto()           # Git仓库
    URL = auto()           # 直接URL下载


@dataclass
class DependencySpec:
    """第三方库依赖规格"""
    name: str                      # 依赖名称
    version: str                   # 版本号
    dependency_type: DependencyType # 依赖类型
    source_url: Optional[str] = None # 源URL
    parser_name: str = ""          # 发现此依赖的解析器
    depth: int = 0                 # 依赖深度（0为直接依赖）
    
    @property 
    def unique_key(self) -> str:
        """生成唯一键，用于去重"""
        return f"{self.dependency_type.name}:{self.name}:{self.version}"
        
    @property
    def cache_path(self) -> str:
        """生成缓存路径"""
        # 使用哈希避免路径过长或包含非法字符
        key_hash = hashlib.md5(self.unique_key.encode()).hexdigest()[:12]
        return f"deps_cache/{self.dependency_type.name.lower()}/{key_hash}_{self.name}"


@dataclass
class DependencyResult:
    """依赖拉取结果"""
    spec: DependencySpec
    success: bool
    local_path: Optional[Path] = None
    error: Optional[Exception] = None
    discovered_deps: List[DependencySpec] = field(default_factory=list)  # 发现的新依赖


class DependencyManager:
    """第三方库依赖管理器"""
    
    def __init__(self, cache_root: str = ".depanalyzer_cache", max_depth: int = 3):
        self.cache_root = Path(cache_root)
        self.max_depth = max_depth
        self.lock = threading.RLock()
        
        # 跟踪状态
        self._fetched_deps: Dict[str, DependencyResult] = {}
        self._pending_deps: Set[str] = set()
        self._failed_deps: Set[str] = set()
        
        # 创建缓存目录
        self.cache_root.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Dependency manager initialized with cache at {self.cache_root}")
        logger.info(f"Max dependency depth: {self.max_depth}")
        
    def should_fetch(self, spec: DependencySpec) -> bool:
        """判断是否应该拉取此依赖"""
        with self.lock:
            key = spec.unique_key
            
            # 检查深度限制
            if spec.depth > self.max_depth:
                logger.debug(f"Dependency {spec.name} skipped: depth {spec.depth} > max {self.max_depth}")
                return False
                
            # 检查是否已经处理过
            if key in self._fetched_deps or key in self._pending_deps or key in self._failed_deps:
                logger.debug(f"Dependency {spec.name} already processed or pending")
                return False
                
            # 检查缓存是否存在
            cache_path = self.cache_root / spec.cache_path
            if cache_path.exists():
                logger.info(f"Dependency {spec.name} found in cache at {cache_path}")
                # 标记为已获取
                self._fetched_deps[key] = DependencyResult(
                    spec=spec,
                    success=True,
                    local_path=cache_path
                )
                return False
                
            return True
            
    def mark_pending(self, spec: DependencySpec) -> None:
        """标记依赖为待处理状态"""
        with self.lock:
            self._pending_deps.add(spec.unique_key)
            logger.debug(f"Marked dependency {spec.name} as pending")
            
    def mark_completed(self, result: DependencyResult) -> None:
        """标记依赖拉取完成"""
        with self.lock:
            key = result.spec.unique_key
            self._pending_deps.discard(key)
            
            if result.success:
                self._fetched_deps[key] = result
                logger.info(f"Dependency {result.spec.name} fetched successfully to {result.local_path}")
                
                # 记录新发现的依赖
                if result.discovered_deps:
                    logger.info(f"Discovered {len(result.discovered_deps)} new dependencies from {result.spec.name}")
            else:
                self._failed_deps.add(key)
                logger.error(f"Failed to fetch dependency {result.spec.name}: {result.error}")
                
    def get_fetched_dependencies(self) -> List[DependencyResult]:
        """获取所有已成功拉取的依赖"""
        with self.lock:
            return [result for result in self._fetched_deps.values() if result.success]
            
    def get_all_discovered_dependencies(self) -> List[DependencySpec]:
        """获取所有新发现的依赖（用于递归处理）"""
        with self.lock:
            all_deps = []
            for result in self._fetched_deps.values():
                if result.success:
                    all_deps.extend(result.discovered_deps)
            return all_deps
            
    def get_status(self) -> Dict[str, int]:
        """获取依赖管理状态统计"""
        with self.lock:
            return {
                "fetched": len(self._fetched_deps),
                "pending": len(self._pending_deps), 
                "failed": len(self._failed_deps),
                "total_processed": len(self._fetched_deps) + len(self._failed_deps)
            }


class DependencyFetcher:
    """依赖拉取器基类"""
    
    def __init__(self, dependency_manager: DependencyManager):
        self.dependency_manager = dependency_manager
        
    def fetch(self, spec: DependencySpec) -> DependencyResult:
        """拉取依赖到本地"""
        logger.info(f"Fetching dependency: {spec.name}@{spec.version} (type: {spec.dependency_type.name})")
        
        try:
            # 根据依赖类型选择拉取策略
            if spec.dependency_type == DependencyType.GIT:
                return self._fetch_git_repo(spec)
            elif spec.dependency_type == DependencyType.NPM:
                return self._fetch_npm_package(spec)
            elif spec.dependency_type == DependencyType.MAVEN:
                return self._fetch_maven_dependency(spec)
            elif spec.dependency_type == DependencyType.PIP:
                return self._fetch_pip_package(spec)
            elif spec.dependency_type == DependencyType.URL:
                return self._fetch_url(spec)
            else:
                raise NotImplementedError(f"Dependency type {spec.dependency_type} not supported")
                
        except Exception as e:
            logger.error(f"Failed to fetch {spec.name}: {e}")
            return DependencyResult(spec=spec, success=False, error=e)
            
    def _fetch_git_repo(self, spec: DependencySpec) -> DependencyResult:
        """拉取Git仓库（示例实现）"""
        import subprocess
        
        cache_path = self.dependency_manager.cache_root / spec.cache_path
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 简化的git clone实现
        if spec.source_url:
            cmd = ["git", "clone", spec.source_url, str(cache_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # TODO: 解析新仓库中的依赖
                discovered_deps = self._discover_dependencies_in_path(cache_path, spec.depth + 1)
                
                return DependencyResult(
                    spec=spec,
                    success=True,
                    local_path=cache_path,
                    discovered_deps=discovered_deps
                )
            else:
                raise Exception(f"Git clone failed: {result.stderr}")
        else:
            raise Exception("Git repository URL not provided")
            
    def _fetch_npm_package(self, spec: DependencySpec) -> DependencyResult:
        """拉取NPM包（示例实现）"""
        # TODO: 实现npm包拉取逻辑
        raise NotImplementedError("NPM package fetching not implemented")
        
    def _fetch_maven_dependency(self, spec: DependencySpec) -> DependencyResult:
        """拉取Maven依赖（示例实现）"""
        # TODO: 实现Maven依赖拉取逻辑
        raise NotImplementedError("Maven dependency fetching not implemented")
        
    def _fetch_pip_package(self, spec: DependencySpec) -> DependencyResult:
        """拉取Python包（示例实现）"""
        # TODO: 实现pip包拉取逻辑
        raise NotImplementedError("PIP package fetching not implemented")
        
    def _fetch_url(self, spec: DependencySpec) -> DependencyResult:
        """从URL拉取（示例实现）"""
        # TODO: 实现URL下载逻辑
        raise NotImplementedError("URL fetching not implemented")
        
    def _discover_dependencies_in_path(self, path: Path, depth: int) -> List[DependencySpec]:
        """在指定路径中发现新的依赖（示例实现）"""
        # TODO: 根据文件类型和解析器发现新依赖
        # 这里应该调用对应的解析器来发现依赖
        discovered = []
        
        # 示例：如果是Node.js项目，查找package.json
        package_json = path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    pkg_data = json.load(f)
                    
                # 解析dependencies和devDependencies
                for dep_type in ['dependencies', 'devDependencies']:
                    deps = pkg_data.get(dep_type, {})
                    for dep_name, dep_version in deps.items():
                        discovered.append(DependencySpec(
                            name=dep_name,
                            version=dep_version,
                            dependency_type=DependencyType.NPM,
                            depth=depth
                        ))
            except Exception as e:
                logger.warning(f"Failed to parse package.json in {path}: {e}")
                
        return discovered
