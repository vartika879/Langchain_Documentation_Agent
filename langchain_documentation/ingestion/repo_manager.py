# step1

from pathlib import Path
from git import Repo , GitCommandError
from langchain_documentation.config import REPO_LOCAL_PATH,REPO_URL



def ensure_repo() -> Repo:
    """Clone the repo if it doesn't exist locally, else pull latest changes."""
    if not REPO_LOCAL_PATH.exists():
        print(f"Cloning repo into {REPO_LOCAL_PATH} ...")
        repo = Repo.clone_from(REPO_URL, REPO_LOCAL_PATH)

    else:
        print("Repo already exists, pulling latest changes ...")
        repo = Repo(REPO_LOCAL_PATH)
        try:
            repo.remotes.origin.pull()
        except GitCommandError as e:
            print(f"Pull failed: {e}")
            raise
    return repo


if __name__ == "__main__":
    ensure_repo()