# ingestion/file_finder.py

from pathlib import Path
from langchain_documentation.config import REPO_LOCAL_PATH, TRACKED_PACKAGES


def find_python_files() -> list[tuple[Path, Path]]:
    """Return (file_path, package_root) pairs for all .py files across tracked packages."""
    all_results = []

    for package in TRACKED_PACKAGES:
        package_root = REPO_LOCAL_PATH / package

        if not package_root.exists():
            print(f"Warning: {package_root} does not exist, skipping.")
            continue

        files = package_root.rglob("*.py")
        filtered = [
            f for f in files
            if not any("test" in part.lower() for part in f.parts)
            and "__pycache__" not in f.parts
        ]

        for f in filtered:
            all_results.append((f, package_root))

    return all_results