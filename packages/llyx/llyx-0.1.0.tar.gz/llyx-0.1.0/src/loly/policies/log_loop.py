from pathlib import Path
from typing import List, Dict
import libcst as cst
from loly.policies.base import BasePolicy


class _LogLoopVisitor(cst.CSTVisitor):
    """Internal visitor for log_loop policy."""

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
        self._loop_depth = 0
        self._conditional_depth_stack = []
        self._wrapper = wrapper

    def visit_For(self, node: cst.For) -> None:
        self._loop_depth += 1
        self._conditional_depth_stack.append(0)

    def leave_For(self, node: cst.For) -> None:
        self._loop_depth -= 1
        self._conditional_depth_stack.pop()

    def visit_While(self, node: cst.While) -> None:
        self._loop_depth += 1
        self._conditional_depth_stack.append(0)

    def leave_While(self, node: cst.While) -> None:
        self._loop_depth -= 1
        self._conditional_depth_stack.pop()

    def visit_If(self, node: cst.If) -> None:
        if self._loop_depth > 0 and self._conditional_depth_stack:
            self._conditional_depth_stack[-1] += 1

    def leave_If(self, node: cst.If) -> None:
        if self._loop_depth > 0 and self._conditional_depth_stack:
            self._conditional_depth_stack[-1] -= 1

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        if self._loop_depth > 0 and self._conditional_depth_stack:
            self._conditional_depth_stack[-1] += 1

    def leave_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        if self._loop_depth > 0 and self._conditional_depth_stack:
            self._conditional_depth_stack[-1] -= 1

    def visit_Call(self, node: cst.Call) -> None:
        if self._loop_depth == 0:
            return

        if not self._is_logger_call(node):
            return

        log_level = self._get_log_level(node)
        if not self._should_enforce(log_level):
            return

        if self._is_conditionally_gated():
            return

        self.violations.append(
            {
                "file": str(self.file_path),
                "line": self._get_line_number(node),
                "code": "LY002",
                "message": "Logging in hot loop detected - consider logging before/after loop or using conditional checks",
                "category": "log_loop",
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

    def _is_conditionally_gated(self) -> bool:
        if not self._conditional_depth_stack:
            return False
        return self._conditional_depth_stack[-1] > 0

    def _get_line_number(self, node: cst.CSTNode) -> int:
        try:
            pos = self._wrapper.resolve(cst.metadata.PositionProvider)[node]
            return pos.start.line
        except Exception:
            return 0


class LogLoopPolicy(BasePolicy):
    """Policy to avoid logging in hot loops."""

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
        visitor = _LogLoopVisitor(levels, logger_names, file_path, wrapper)
        wrapper.visit(visitor)
        return visitor.violations
