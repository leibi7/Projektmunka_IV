from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = {"timestamp", "consumption"}


def load_consumption_csv(path: str | Path, tz: str | None = None) -> pd.DataFrame:
    """Load consumption CSV with timestamp and consumption columns.

    Parameters
    ----------
    path: str | Path
        Path to CSV file.
    tz: Optional[str]
        Target timezone (e.g., "Europe/Budapest"). If provided, timestamps are localized/converted.
    """
    path = Path(path)
    logger.info("Loading consumption data from %s", path)
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    if tz:
        df["timestamp"] = df["timestamp"].dt.tz_convert(tz)
    df = df.sort_values("timestamp").reset_index(drop=True)
    if df["timestamp"].isna().any():
        raise ValueError("Invalid timestamps encountered during parsing.")
    return df


def save_dataframe(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved dataframe to %s", path)


def load_profile_metadata(path: str | Path) -> Optional[pd.DataFrame]:
    if not Path(path).exists():
        return None
    return pd.read_csv(path)
