from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
from transformers import pipeline

from energy_app.models.base import BaseForecaster

logger = logging.getLogger(__name__)


class GraniteTTMForecaster(BaseForecaster):
    def __init__(self, model_id: str = "ibm-granite/granite-timeseries-ttm-r1"):
        self.model_id = model_id
        self._pipeline = pipeline(
            task="time-series-forecasting",
            model=self.model_id,
        )

    def fit(self, X: Any, y: Any) -> None:  # pragma: no cover - zero-shot
        logger.info("Granite TTM operates zero-shot; fit is a no-op.")

    def predict(self, X: np.ndarray, horizon: int, exog: Any | None = None) -> np.ndarray:
        # Expect X shape (context_length,) or (batch, context_length)
        context = X[-1] if X.ndim > 1 else X
        result = self._pipeline(
            inputs=context.tolist(),
            prediction_length=horizon,
        )
        preds = np.array(result[0]["prediction"])
        return preds

    def save(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.info("Granite TTM uses hosted weights; nothing to persist locally beyond config.")

    @classmethod
    def load(cls, path: str) -> "GraniteTTMForecaster":
        return cls()
