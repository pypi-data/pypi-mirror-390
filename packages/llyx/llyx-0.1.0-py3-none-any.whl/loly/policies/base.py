from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict


class BasePolicy(ABC):
    @classmethod
    @abstractmethod
    def check(
        cls,
        code: str,
        file_path: Path,
        levels: List[str],
        logger_names: List[str],
        **kwargs
    ) -> List[Dict]:
        """Check code for policy violations.

        Args:
            code: Python source code to analyze
            file_path: Path to the file being analyzed
            levels: Log levels to enforce (e.g., ["error", "info"])
            logger_names: Logger variable names to detect (e.g., ["logger", "logging"])
            **kwargs: Policy-specific configuration (e.g., delimiter for ConsistentKVPolicy)

        Returns:
            List of violation dictionaries with keys:
                - file: str - File path
                - line: int - Line number
                - message: str - Violation description
        """
        pass
