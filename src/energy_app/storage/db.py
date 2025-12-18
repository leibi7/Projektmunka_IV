from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable


class Database:
    def __init__(self, url: str):
        if url.startswith("sqlite:///"):
            path = url.replace("sqlite:///", "")
        else:
            path = url
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        with sqlite3.connect(self.path) as conn, open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
            conn.commit()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def execute(self, func: Callable[[sqlite3.Connection], None]) -> None:
        with self.connect() as conn:
            func(conn)
            conn.commit()
