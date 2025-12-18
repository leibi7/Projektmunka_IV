from __future__ import annotations

import logging
from typing import Iterable, List

import pandas as pd

logger = logging.getLogger(__name__)


DEFAULT_LAGS = [1, 2, 3, 24, 48, 168]
ROLLING_WINDOWS = [24, 168]


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
    return df


def add_lag_features(df: pd.DataFrame, lags: Iterable[int] = DEFAULT_LAGS) -> pd.DataFrame:
    df = df.copy()
    for lag in lags:
        df[f"lag_{lag}"] = df["consumption"].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, windows: Iterable[int] = ROLLING_WINDOWS) -> pd.DataFrame:
    df = df.copy()
    for window in windows:
        df[f"roll_mean_{window}"] = df["consumption"].rolling(window=window, min_periods=1).mean()
        df[f"roll_std_{window}"] = df["consumption"].rolling(window=window, min_periods=1).std().fillna(0)
    return df


def build_baseline_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df_feat = add_time_features(df)
    df_feat = add_lag_features(df_feat)
    df_feat = add_rolling_features(df_feat)
    df_feat = df_feat.dropna().reset_index(drop=True)
    logger.info("Built baseline feature matrix with shape %s", df_feat.shape)
    return df_feat


def feature_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if c not in {"timestamp", "consumption"}]
