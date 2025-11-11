import ast
import re
from pathlib import Path
from typing import List, Dict
import libcst as cst
from loly.policies.base import BasePolicy


class _ConsistentKVVisitor(cst.CSTVisitor):

    def __init__(
        self,
        levels: List[str],
        logger_names: List[str],
        file_path: Path,
        wrapper: cst.MetadataWrapper,
        delimiter: str,
    ):
        self.levels = levels
        self.logger_names = logger_names
        self.file_path = file_path
        self.violations = []
        self._wrapper = wrapper
        self.delimiter = delimiter

        key_pattern = r"[a-zA-Z_][a-zA-Z0-9_]*"
        self.key_value_pattern = re.compile(
            rf"{key_pattern}\s*{re.escape(self.delimiter)}\s*$"
        )
        self.PLACEHOLDER_RE = re.compile(r"%[sdifrxegG]")

    def visit_Call(self, node: cst.Call) -> None:
        if not self._is_logger_call(node):
            return

        log_level = self._get_log_level(node)
        if not self._should_enforce(log_level):
            return

        self._check_variables_have_keys(node)

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

    def _check_variables_have_keys(self, node: cst.Call) -> None:
        if not node.args:
            return
        
        log_msg_node = node.args[0].value
        
        if isinstance(log_msg_node, cst.FormattedString):
            self._check_fstring(log_msg_node)
        
        if isinstance(log_msg_node, cst.SimpleString) and len(node.args) > 1:
            self._check_percent_string(log_msg_node)

    
    def _check_percent_string(self, node: cst.SimpleString) -> bool:
        """Analyzes a %-style format string for orphan placeholders."""
        try:
            log_template = ast.literal_eval(node.value)
        except (ValueError, SyntaxError):
            return

        last_match_end = 0
        
        for match in self.PLACEHOLDER_RE.finditer(log_template):
            text_before = log_template[last_match_end:match.start()]
            
            if not self.key_value_pattern.search(text_before):
                self.violations.append(
                    {
                        "file": str(self.file_path),
                        "line": self._get_line_number(node),
                        "code": "LY003",
                        "message": f"Variable placeholder '{match.group(0)}' must be preceded by key{self.delimiter}",
                        "category": "consistent_kv",
                        "severity": "fail",
                    }
                )
                return False

            last_match_end = match.end()
    
    def _check_fstring(self, node: cst.FormattedString):
        """Analyzes an f-string for orphan variables."""

        for i, part in enumerate(node.parts):
            if not isinstance(part, cst.FormattedStringExpression):
                continue

            if part.equal is not None:
                continue

            # FAIL: Orphan at the start: f"{var}..."
            if i == 0:
                self.violations.append({
                    "file": str(self.file_path),
                    "line": self._get_line_number(node),
                    "code": "LY003",
                    "message": "Orphan variable at start of f-string",
                    "category": "consistent_kv",
                    "severity": "fail",
                })
                continue

            prev_part = node.parts[i - 1]

            if not isinstance(prev_part, cst.FormattedStringText):
                self.violations.append({
                    "file": str(self.file_path),
                    "line": self._get_line_number(node),
                    "code": "LY003",
                    "message": "Orphan variable follows another expression",
                    "category": "consistent_kv",
                    "severity": "fail",
                })
                continue

            text_before = prev_part.value

            if not self.key_value_pattern.search(text_before):
                self.violations.append({
                    "file": str(self.file_path),
                    "line": self._get_line_number(node),
                    "code": "LY003",
                    "message": f"Variable lacks a key and '{self.delimiter}' delimiter",
                    "category": "consistent_kv",
                    "severity": "fail",
                })

    def _get_line_number(self, node: cst.CSTNode) -> int:
        try:
            pos = self._wrapper.resolve(cst.metadata.PositionProvider)[node]
            return pos.start.line
        except Exception:
            return 0


class ConsistentKVPolicy(BasePolicy):
    @classmethod
    def check(
        cls,
        code: str,
        file_path: Path,
        levels: List[str],
        logger_names: List[str],
        **kwargs
    ) -> List[Dict]:
        if "delimiter" not in kwargs:
            raise ValueError(
                "ConsistentKVPolicy requires 'delimiter' parameter in kwargs. "
                "This should be provided by the configuration/schema layer."
            )

        delimiter = kwargs["delimiter"]

        module = cst.parse_module(code)
        wrapper = cst.MetadataWrapper(module)
        visitor = _ConsistentKVVisitor(
            levels, logger_names, file_path, wrapper, delimiter
        )
        wrapper.visit(visitor)
        return visitor.violations
