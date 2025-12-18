from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional
import time


class WeatherCache:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def get(self, key: str) -> Optional[dict]:
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.execute("SELECT value FROM cache WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            return json.loads(row[0])
        finally:
            conn.close()

    def set(self, key: str, value: dict) -> None:
        conn = sqlite3.connect(self.path)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, created_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), time.time()),
            )
            conn.commit()
        finally:
            conn.close()
