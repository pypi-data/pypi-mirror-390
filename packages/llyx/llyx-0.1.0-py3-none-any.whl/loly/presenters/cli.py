import os
from collections import defaultdict
from typing import List
from colorama import Fore, Style, init
from loly.violation import Violation
from loly.presenters.base import ViolationPresenter


class CLIPresenter(ViolationPresenter):
    """CLI presenter with file grouping, colors, and summary statistics."""
    def __init__(self, use_color: bool = None):
        init(autoreset=True)  # Initialize colorama

        if use_color is None:
            # Auto-detect: respect NO_COLOR and check if stdout is a TTY
            self.use_color = (
                not os.environ.get("NO_COLOR")
                and hasattr(os.sys.stdout, "isatty")
                and os.sys.stdout.isatty()
            )
        else:
            self.use_color = use_color

    def present(self, violations: List[Violation]) -> str:
        if not violations:
            return self._colorize("No violations found!", Fore.GREEN)

        # Group violations by file
        grouped = self._group_by_file(violations)

        lines = []

        # Output grouped violations
        for file_path, file_violations in grouped.items():
            lines.append(self._colorize(file_path, Fore.CYAN, Style.BRIGHT))
            for violation in file_violations:
                lines.append(self._format_violation(violation))
            lines.append("")  # Empty line between files

        # Add summary
        lines.append(self._format_summary(violations, len(grouped)))

        return "\n".join(lines)

    def _group_by_file(self, violations: List[Violation]) -> dict:
        grouped = defaultdict(list)
        for violation in violations:
            grouped[violation.file].append(violation)
        return dict(grouped)

    def _format_violation(self, violation: Violation) -> str:
        if violation.severity == "error":
            severity_color = Fore.RED
        elif violation.severity == "warning":
            severity_color = Fore.YELLOW
        else:
            severity_color = Fore.BLUE

        line_info = f"  {violation.line}:0"
        code = self._colorize(violation.code, severity_color, Style.BRIGHT)
        severity = self._colorize(f"[{violation.severity.upper()}]", severity_color)
        message = violation.message

        return f"{line_info:8} {code:20} {severity:20} {message}"

    def _format_summary(self, violations: List[Violation], file_count: int) -> str:
        lines = []

        lines.append(self._colorize("─" * 60, Fore.CYAN))

        # File and violation counts
        lines.append(
            f"{file_count} file{'s' if file_count != 1 else ''} with violations"
        )
        lines.append(
            f"{len(violations)} total violation{'s' if len(violations) != 1 else ''}"
        )

        # Count by error code
        code_counts = defaultdict(int)
        for violation in violations:
            code_counts[violation.code] += 1

        for code, count in sorted(code_counts.items()):
            lines.append(f"  {code}: {count} violation{'s' if count != 1 else ''}")

        return "\n".join(lines)

    def _colorize(self, text: str, *colors) -> str:
        if not self.use_color:
            return text

        color_prefix = "".join(colors)
        return f"{color_prefix}{text}{Style.RESET_ALL}"
