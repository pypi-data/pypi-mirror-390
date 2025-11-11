import argparse
import sys
from pathlib import Path
from loly.linter import Linter
from loly.presenters.cli import CLIPresenter


def main():
    parser = argparse.ArgumentParser(
        prog="loly", description="A Python logging linter that enforces best practices"
    )
    parser.add_argument("path", type=Path, help="file or directory to lint")
    parser.add_argument(
        "--config",
        type=Path,
        metavar="PATH",
        help="path to config file (default: loly.yml)",
    )

    args = parser.parse_args()

    linter = Linter(args.config)
    violations = linter.lint(args.path)

    presenter = CLIPresenter()
    output = presenter.present(violations)
    print(output)

    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()
