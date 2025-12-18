from __future__ import annotations

import numpy as np
import pandas as pd


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return float(np.mean(np.abs((y_true - y_pred) / np.clip(np.abs(y_true), 1e-6, None))) * 100)


def peak_error(y_true, y_pred):
    return float(np.max(np.abs(y_true - y_pred)))


def evaluate_series(y_true: pd.Series, y_pred: pd.Series) -> dict:
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "mape": mape(y_true, y_pred),
        "peak_error": peak_error(y_true, y_pred),
    }
