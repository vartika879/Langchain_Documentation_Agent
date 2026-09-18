# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
REPO_LOCAL_PATH = BASE_DIR / "data" / "langchain_repo"
DB_PATH = BASE_DIR / "data" / "fingerprints.db"

REPO_URL = "https://github.com/langchain-ai/langchain.git"

TRACKED_PACKAGES = [
    "libs/core",
    "libs/langchain",
    "libs/partners/openai",
    "libs/partners/anthropic",
]

DATABASE_URL = f"sqlite:///{DB_PATH}"