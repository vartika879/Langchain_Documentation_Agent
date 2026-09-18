# ingestion/file_finder.py

from pathlib import Path
#from config import REPO_LOCAL_PATH, TRACKED_PACKAGE
from langchain_documentation.config import REPO_LOCAL_PATH, TRACKED_PACKAGE


def find_python_files() -> list[Path]:
    """Return all .py files inside the tracked package, excluding tests."""
    target_dir = REPO_LOCAL_PATH / TRACKED_PACKAGE

    all_files = target_dir.rglob("*.py")

    filtered = [
        f for f in all_files
        if "test" not in f.parts and "__pycache__" not in f.parts
    ]

    return filtered


if __name__ == "__main__":
    
    files = find_python_files()
    print(f"Found {len(files)} files")
    print(files[:5])  # pehli 5 dikhao sample ke liye