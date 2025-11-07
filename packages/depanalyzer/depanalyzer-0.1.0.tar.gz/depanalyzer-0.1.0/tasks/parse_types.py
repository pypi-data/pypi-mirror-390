
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any

@dataclass
class ParseTask:
    repo_root: str
    parser_name: str
    code_files: List[Path] = field(default_factory=list)
    config_files: List[Path] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
