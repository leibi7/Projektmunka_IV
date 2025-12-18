from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from energy_app.models.base import BaseForecaster
from energy_app.data.features import feature_columns

logger = logging.getLogger(__name__)

try:
    import lightgbm as lgb
except ImportError:  # pragma: no cover - fallback path
    lgb = None


class BaselineForecaster(BaseForecaster):
    def __init__(self):
        if lgb:
            self.model = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05)
            logger.info("Using LightGBM regressor")
        else:
            self.model = HistGradientBoostingRegressor(max_depth=6)
            logger.info("Using sklearn HistGradientBoostingRegressor")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame, horizon: int, exog=None) -> np.ndarray:
        try:
            preds = self.model.predict(X.tail(horizon))
            return preds
        except Exception:  # pragma: no cover - fallback for demo before training
            last = X[\"consumption\"].iloc[-1] if \"consumption\" in X.columns else 0.0
            return np.full(horizon, last)

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info("Saved baseline model to %s", path)

    @classmethod
    def load(cls, path: str) -> "BaselineForecaster":
        obj = cls()
        obj.model = joblib.load(path)
        return obj

    @staticmethod
    def build_training_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        X = df[feature_columns(df)]
        y = df["consumption"]
        return X, y
