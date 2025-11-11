from pathlib import Path
from typing import List, Dict
import libcst as cst
from loly.policies.base import BasePolicy


class _ExceptionExcInfoVisitor(cst.CSTVisitor):
    """Internal visitor for exception_exc_info policy."""

    def __init__(
        self,
        levels: List[str],
        logger_names: List[str],
        file_path: Path,
        wrapper: cst.MetadataWrapper,
    ):
        self.levels = levels
        self.logger_names = logger_names
        self.file_path = file_path
        self.violations = []
        self._in_except_handler = False
        self._wrapper = wrapper

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        self._in_except_handler = True

    def leave_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        self._in_except_handler = False

    def visit_Call(self, node: cst.Call) -> None:
        if not self._in_except_handler:
            return

        if not self._is_logger_call(node):
            return

        log_level = self._get_log_level(node)
        if not self._should_enforce(log_level):
            return

        if not self._has_exc_info_true(node):
            self.violations.append(
                {
                    "file": str(self.file_path),
                    "line": self._get_line_number(node),
                    "code": "LY001",
                    "message": "Missing exc_info=True in exception handler",
                    "category": "exception_exc_info",
                    "severity": "fail",
                }
            )

    def _is_logger_call(self, node: cst.Call) -> bool:
        if not isinstance(node.func, cst.Attribute):
            return False

        if isinstance(node.func.value, cst.Name):
            return node.func.value.value in self.logger_names

        return False

    def _get_log_level(self, node: cst.Call) -> str:
        if isinstance(node.func, cst.Attribute):
            return node.func.attr.value
        return ""

    def _should_enforce(self, log_level: str) -> bool:
        if "any" in self.levels:
            return True
        return log_level in self.levels

    def _has_exc_info_true(self, node: cst.Call) -> bool:
        for arg in node.args:
            if isinstance(arg.keyword, cst.Name) and arg.keyword.value == "exc_info":
                if isinstance(arg.value, cst.Name) and arg.value.value == "True":
                    return True
                if isinstance(arg.value, cst.Integer) and arg.value.value == "1":
                    return True
                return False
        return False

    def _get_line_number(self, node: cst.CSTNode) -> int:
        try:
            pos = self._wrapper.resolve(cst.metadata.PositionProvider)[node]
            return pos.start.line
        except Exception:
            return 0


class ExceptionExcInfoPolicy(BasePolicy):
    """Policy to enforce exc_info=True in exception handlers."""

    @classmethod
    def check(
        cls,
        code: str,
        file_path: Path,
        levels: List[str],
        logger_names: List[str],
        **kwargs
    ) -> List[Dict]:
        module = cst.parse_module(code)
        wrapper = cst.MetadataWrapper(module)
        visitor = _ExceptionExcInfoVisitor(levels, logger_names, file_path, wrapper)
        wrapper.visit(visitor)
        return visitor.violations
