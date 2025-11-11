from pathlib import Path
from typing import List, Dict, Optional
import yaml
from loly.policies.exception_exc_info import ExceptionExcInfoPolicy
from loly.policies.log_loop import LogLoopPolicy
from loly.file_collector import FileCollector
from loly.violation import Violation


class Linter:
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.logger_names = self.config.get(
            "logger_names", ["logging", "logger", "log"]
        )
        self.file_collector = FileCollector(self.config)

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def lint(self, path: Path) -> List[Violation]:
        """Lint Python files at given path.

        Args:
            path: File or directory to lint

        Returns:
            List of Violation objects
        """
        files = self.file_collector.collect_files(path)
        return self._lint_sequential(files)

    def _lint_sequential(self, files: List[Path]) -> List[Violation]:
        """Lint files sequentially.

        Args:
            files: List of file paths to lint

        Returns:
            List of Violation objects
        """
        violations = []
        for file_path in files:
            violations.extend(self._lint_file(file_path))
        return violations

    def _lint_parallel(self, files: List[Path], jobs: int) -> List[Violation]:
        """Lint files in parallel (placeholder for future implementation).

        Args:
            files: List of file paths to lint
            jobs: Number of parallel workers

        Returns:
            List of Violation objects
        """
        # TODO: Implement parallel linting using ProcessPoolExecutor
        return self._lint_sequential(files)

    def _lint_file(self, file_path: Path) -> List[Violation]:
        """Lint a single file.

        Args:
            file_path: Path to file to lint

        Returns:
            List of Violation objects
        """
        violation_dicts = []

        try:
            with open(file_path) as f:
                code = f.read()

            if "exception_exc_info" in self.config:
                policy_config = self.config["exception_exc_info"]
                levels = policy_config.get("levels", ["error"])
                violation_dicts.extend(
                    ExceptionExcInfoPolicy.check(
                        code, file_path, levels, self.logger_names
                    )
                )

            if "log_loop" in self.config:
                policy_config = self.config["log_loop"]
                levels = policy_config.get("levels", ["info", "debug"])
                violation_dicts.extend(
                    LogLoopPolicy.check(code, file_path, levels, self.logger_names)
                )

        except Exception:
            pass

        # Convert dicts to Violation objects
        return [Violation.from_dict(v) for v in violation_dicts]
