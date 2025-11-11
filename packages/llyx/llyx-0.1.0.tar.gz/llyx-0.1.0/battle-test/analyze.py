#!/usr/bin/env python3
"""Battle test loly against real-world Python projects."""

import subprocess
import json
import shutil
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class RepoStats:
    name: str
    url: str
    clone_success: bool
    total_py_files: int
    ly001_count: int
    ly002_count: int
    total_violations: int
    files_with_violations: int
    sample_violations: List[str]
    error: str = ""


REPOS = [
    ("fastapi", "https://github.com/tiangolo/fastapi.git"),
    ("airflow", "https://github.com/apache/airflow.git"),
    ("superset", "https://github.com/apache/superset.git"),
    ("sentry", "https://github.com/getsentry/sentry.git"),
    ("prefect", "https://github.com/PrefectHQ/prefect.git"),
    ("mlflow", "https://github.com/mlflow/mlflow.git"),
    ("dagster", "https://github.com/dagster-io/dagster.git"),
    ("flower", "https://github.com/mher/flower.git"),
    ("locust", "https://github.com/locustio/locust.git"),
    ("mitmproxy", "https://github.com/mitmproxy/mitmproxy.git"),
]

BATTLE_TEST_DIR = Path(__file__).parent
REPOS_DIR = BATTLE_TEST_DIR / "repos"


def clone_repo(name: str, url: str) -> bool:
    """Shallow clone a repository."""
    repo_path = REPOS_DIR / name
    if repo_path.exists():
        shutil.rmtree(repo_path)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(repo_path)],
            capture_output=True,
            check=True,
            timeout=300,
        )
        return True
    except Exception as e:
        print(f"Failed to clone {name}: {e}")
        return False


def count_py_files(repo_path: Path) -> int:
    """Count total Python files in repo."""
    return len(list(repo_path.rglob("*.py")))


def run_loly(repo_path: Path) -> Dict:
    """Run loly on a repository and parse output."""
    try:
        config_path = BATTLE_TEST_DIR / "loly.yml"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "loly.cli",
                str(repo_path),
                f"--config={config_path}",
            ],
            capture_output=True,
            text=True,
            timeout=600,
            env={"NO_COLOR": "1"},
        )

        output = result.stdout + result.stderr

        # Parse violations
        ly001_count = output.count("LY001")
        ly002_count = output.count("LY002")

        # Extract sample violations (first 5 lines with LY001 or LY002)
        samples = []
        for line in output.split("\n"):
            if "LY001" in line or "LY002" in line:
                samples.append(line.strip())
                if len(samples) >= 5:
                    break

        # Parse summary
        total_violations = 0
        files_with_violations = 0

        for line in output.split("\n"):
            if "total violation" in line:
                parts = line.split()
                if parts:
                    try:
                        total_violations = int(parts[0])
                    except:
                        pass
            if "files with violations" in line:
                parts = line.split()
                if parts:
                    try:
                        files_with_violations = int(parts[0])
                    except:
                        pass

        return {
            "ly001_count": ly001_count,
            "ly002_count": ly002_count,
            "total_violations": total_violations,
            "files_with_violations": files_with_violations,
            "sample_violations": samples,
        }

    except Exception as e:
        return {
            "ly001_count": 0,
            "ly002_count": 0,
            "total_violations": 0,
            "files_with_violations": 0,
            "sample_violations": [],
            "error": str(e),
        }


def analyze_repo(name: str, url: str) -> RepoStats:
    """Analyze a single repository."""
    print(f"\n{'=' * 60}")
    print(f"Analyzing: {name}")
    print(f"{'=' * 60}")

    # Clone
    print(f"Cloning {name}...")
    clone_success = clone_repo(name, url)

    if not clone_success:
        return RepoStats(
            name=name,
            url=url,
            clone_success=False,
            total_py_files=0,
            ly001_count=0,
            ly002_count=0,
            total_violations=0,
            files_with_violations=0,
            sample_violations=[],
            error="Clone failed",
        )

    repo_path = REPOS_DIR / name

    # Count files
    print("Counting Python files...")
    total_py_files = count_py_files(repo_path)
    print(f"Found {total_py_files} Python files")

    # Run loly
    print("Running loly...")
    results = run_loly(repo_path)

    print(f"LY001: {results['ly001_count']}")
    print(f"LY002: {results['ly002_count']}")
    print(f"Total violations: {results['total_violations']}")

    return RepoStats(
        name=name,
        url=url,
        clone_success=True,
        total_py_files=total_py_files,
        ly001_count=results["ly001_count"],
        ly002_count=results["ly002_count"],
        total_violations=results["total_violations"],
        files_with_violations=results["files_with_violations"],
        sample_violations=results["sample_violations"],
        error=results.get("error", ""),
    )


def cleanup_repos():
    """Remove all cloned repositories."""
    if REPOS_DIR.exists():
        print(f"\nCleaning up {REPOS_DIR}...")
        shutil.rmtree(REPOS_DIR)
        print("Cleanup complete!")


def main():
    """Main analysis workflow."""
    REPOS_DIR.mkdir(exist_ok=True)

    all_stats = []

    for name, url in REPOS:
        stats = analyze_repo(name, url)
        all_stats.append(stats)

    # Save raw data
    results_file = BATTLE_TEST_DIR / "results.json"
    with open(results_file, "w") as f:
        json.dump([asdict(s) for s in all_stats], f, indent=2)

    print(f"\n{'=' * 60}")
    print("Results saved to results.json")
    print(f"{'=' * 60}")

    # Cleanup
    cleanup_repos()

    return all_stats


if __name__ == "__main__":
    main()
