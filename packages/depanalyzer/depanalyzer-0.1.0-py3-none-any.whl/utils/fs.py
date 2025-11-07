
from pathlib import Path
from typing import Iterable, List

def walk_files(root: str, globs: Iterable[str]) -> List[Path]:
    root_path = Path(root)
    results: List[Path] = []
    for pattern in globs:
        results.extend(root_path.rglob(pattern))
    uniq = []
    seen = set()
    for p in results:
        rp = p.resolve()
        if rp not in seen and rp.is_file():
            uniq.append(rp)
            seen.add(rp)
    return uniq
