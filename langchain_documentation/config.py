# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
REPO_LOCAL_PATH = BASE_DIR / "data" / "langchain_repo"
DB_PATH = BASE_DIR / "data" / "fingerprints.db"

# --- Source repo ---
REPO_URL = "https://github.com/langchain-ai/langchain.git"
TRACKED_PACKAGE = "libs/core"

# --- Database ---
DATABASE_URL = f"sqlite:///{DB_PATH}"