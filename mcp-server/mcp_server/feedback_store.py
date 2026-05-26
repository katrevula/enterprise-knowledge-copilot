from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class FeedbackStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    comment TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    def record(self, message_id: str, rating: str, comment: str | None = None) -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO feedback (message_id, rating, comment, created_at) VALUES (?, ?, ?, ?)",
                (message_id, rating, comment, created_at),
            )
        return {
            "feedback_id": cursor.lastrowid,
            "message_id": message_id,
            "rating": rating,
            "created_at": created_at,
        }

