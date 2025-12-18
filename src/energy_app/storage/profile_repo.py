from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sqlite3

from energy_app.storage.db import Database


@dataclass
class Profile:
    user_id: str
    location_text: str
    lat: float
    lon: float
    area_m2: float
    occupants: int
    heating_type: str | None = None


class ProfileRepository:
    def __init__(self, db: Database):
        self.db = db

    def upsert_user(self, user_id: str, display_name: str | None = None) -> None:
        def _op(conn: sqlite3.Connection) -> None:
            conn.execute(
                "INSERT OR IGNORE INTO users (id, display_name) VALUES (?, ?)",
                (user_id, display_name),
            )

        self.db.execute(_op)

    def upsert_profile(self, profile: Profile) -> None:
        def _op(conn: sqlite3.Connection) -> None:
            conn.execute(
                """
                INSERT INTO profiles (user_id, location_text, lat, lon, area_m2, occupants, heating_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    location_text=excluded.location_text,
                    lat=excluded.lat,
                    lon=excluded.lon,
                    area_m2=excluded.area_m2,
                    occupants=excluded.occupants,
                    heating_type=excluded.heating_type,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    profile.user_id,
                    profile.location_text,
                    profile.lat,
                    profile.lon,
                    profile.area_m2,
                    profile.occupants,
                    profile.heating_type,
                ),
            )

        self.db.execute(_op)

    def get_profile(self, user_id: str) -> Optional[Profile]:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT user_id, location_text, lat, lon, area_m2, occupants, heating_type FROM profiles WHERE user_id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return Profile(*row)
