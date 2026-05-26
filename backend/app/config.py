from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings:
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    database_url: Path = Path(os.getenv("BACKEND_DATABASE_URL", REPO_ROOT / "storage" / "copilot.db"))
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]


settings = Settings()

