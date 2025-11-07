
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, List, Optional
from threading import Lock
from utils.graph import GraphManager
from dependencies.dependency_manager import DependencySpec

class BaseParser(ABC):
    NAME: str = "base"
    CODE_GLOBS: List[str] = []
    CONFIG_GLOBS: List[str] = []

    def __init__(self, repo_root: str, shared_graph: Optional[GraphManager] = None) -> None:
        self.repo_root = repo_root
        self.shared_graph = shared_graph
        # Thread-safe lock for graph operations
        self.graph_lock = Lock()

    @classmethod
    def discover_code_files(cls, repo_root: str) -> List[Path]:
        from utils.fs import walk_files
        return walk_files(repo_root, cls.CODE_GLOBS)

    @classmethod
    def discover_config_files(cls, repo_root: str) -> List[Path]:
        from utils.fs import walk_files
        return walk_files(repo_root, cls.CONFIG_GLOBS)
    
    def discover_dependencies(self, files: List[Path]) -> List[DependencySpec]:
        """
        发现第三方库依赖的抽象接口。
        
        子类必须重写此方法来实现特定语言的依赖检测逻辑，包括：
        1. 解析源代码文件，提取导入/包含语句
        2. 区分本地依赖和第三方依赖  
        3. 将第三方依赖转换为DependencySpec对象
        
        Args:
            files: 需要分析依赖的文件列表
            
        Returns:
            只包含第三方依赖的DependencySpec列表（本地依赖应直接加入依赖图）
        """
        return []  # 默认实现：不发现任何第三方依赖
    
    def post_process(self, shared_graph: GraphManager) -> None:
        """
        可选的后处理钩子，在所有解析器完成后调用。
        子类可以重写此方法来处理跨解析器依赖关系。
        
        Args:
            shared_graph: 共享的依赖图，包含所有解析器的结果
        """
        pass

def normalize_node_id(file_path: Path, repo_root: str, target_name: str = None) -> str:
    """
    统一的节点ID标准化函数
    
    Args:
        file_path: 文件路径
        repo_root: 仓库根目录
        target_name: 可选的目标名称（用于CMake目标）
    
    Returns:
        标准化的节点ID: //相对路径 或 //相对路径:目标名
    """
    repo_path = Path(repo_root)
    try:
        rel_path = file_path.relative_to(repo_path)
        base_id = f"//{rel_path.as_posix()}"
        return f"{base_id}:{target_name}" if target_name else base_id
    except ValueError:
        # 文件在仓库外，使用external前缀
        base_id = f"//external:{file_path.as_posix()}"
        return f"{base_id}:{target_name}" if target_name else base_id

class BaseCodeParser(BaseParser):
    MAX_WORKERS: int = 8

    def parse_files(self, files: Iterable[Path], shared_graph: GraphManager) -> None:
        """Parse files and update the shared graph in-place."""
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as ex:
            futs = {ex.submit(self.parse_file, f, shared_graph): f for f in files}
            for fut in as_completed(futs):
                # Just wait for completion, no need to collect results
                fut.result()

    @abstractmethod
    def parse_file(self, file_path: Path, shared_graph: GraphManager) -> None:
        """Parse a single file and update the shared graph in-place."""
        raise NotImplementedError

class BaseConfigParser(BaseParser):
    MAX_WORKERS: int = 4

    def parse_files(self, files: Iterable[Path], shared_graph: GraphManager) -> None:
        """Parse files and update the shared graph in-place."""
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as ex:
            futs = {ex.submit(self.parse_file, f, shared_graph): f for f in files}
            for fut in as_completed(futs):
                # Just wait for completion, no need to collect results
                fut.result()

    @abstractmethod
    def parse_file(self, file_path: Path, shared_graph: GraphManager) -> None:
        """Parse a single file and update the shared graph in-place."""
        raise NotImplementedError
