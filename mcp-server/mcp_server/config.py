from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]

HF_CACHE_DIR = Path(os.getenv("HF_HOME", REPO_ROOT / "storage" / "huggingface"))
HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR))
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(HF_CACHE_DIR / "sentence-transformers"))

DATA_DIR = Path(os.getenv("HR_POLICY_DATA_DIR", REPO_ROOT / "data" / "hr_policies"))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", REPO_ROOT / "storage" / "chroma"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "hr_policy_chunks")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
FEEDBACK_DB = Path(os.getenv("MCP_FEEDBACK_DB", REPO_ROOT / "storage" / "mcp_feedback.db"))
