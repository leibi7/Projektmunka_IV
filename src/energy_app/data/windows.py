from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def sliding_window(series: pd.Series, window: int, horizon: int) -> Tuple[np.ndarray, np.ndarray]:
    values = series.values
    X, y = [], []
    for i in range(len(values) - window - horizon + 1):
        X.append(values[i : i + window])
        y.append(values[i + window : i + window + horizon])
    X_arr = np.array(X)
    y_arr = np.array(y)
    logger.info("Built sliding windows: X=%s, y=%s", X_arr.shape, y_arr.shape)
    return X_arr, y_arr


@dataclass
class WindowConfig:
    window: int = 168
    horizon: int = 24


def build_transformer_windows(df: pd.DataFrame, cfg: WindowConfig) -> Tuple[np.ndarray, np.ndarray]:
    series = df["consumption"]
    return sliding_window(series, cfg.window, cfg.horizon)
