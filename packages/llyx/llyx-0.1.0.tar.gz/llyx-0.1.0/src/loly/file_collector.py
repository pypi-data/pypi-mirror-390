from pathlib import Path
from typing import List, Dict


class FileCollector:
    """Discovers and filters Python files for linting."""

    def __init__(self, config: Dict):
        self.config = config

    def collect_files(self, path: Path) -> List[Path]:
        files = []

        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                if self._should_check_file(py_file):
                    files.append(py_file)

        return files

    def _should_check_file(self, file_path: Path) -> bool:
        path_str = str(file_path)

        exclude_patterns = self.config.get("exclude", [])
        for pattern in exclude_patterns:
            if pattern in path_str:
                return False

        return True
