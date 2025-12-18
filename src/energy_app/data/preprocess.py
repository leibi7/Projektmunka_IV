from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Tuple

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class SplitConfig:
    train_frac: float = 0.7
    val_frac: float = 0.15


def fill_and_resample(df: pd.DataFrame, tz: str | None = None, freq: str = "1H") -> pd.DataFrame:
    """Ensure hourly cadence, handling timezone and gaps."""
    df = df.copy()
    if tz:
        df["timestamp"] = df["timestamp"].dt.tz_convert(tz)
    df = df.set_index("timestamp").sort_index()
    full_range = pd.date_range(df.index.min(), df.index.max(), freq=freq, tz=df.index.tz)
    df = df.reindex(full_range)
    df["consumption"] = df["consumption"].interpolate(limit_direction="both")
    df["consumption"] = df["consumption"].fillna(method="ffill")
    df = df.reset_index().rename(columns={"index": "timestamp"})
    logger.info("Resampled to %s frequency with %d rows", freq, len(df))
    return df


def time_based_split(df: pd.DataFrame, config: SplitConfig | None = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cfg = config or SplitConfig()
    if cfg.train_frac + cfg.val_frac >= 1:
        raise ValueError("train_frac + val_frac must be < 1")
    n = len(df)
    train_end = int(n * cfg.train_frac)
    val_end = train_end + int(n * cfg.val_frac)
    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]
    logger.info("Split data into train=%d, val=%d, test=%d", len(train), len(val), len(test))
    return train, val, test
