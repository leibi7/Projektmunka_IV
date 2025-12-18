from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import PatchTSTForPrediction, PatchTSTConfig

from energy_app.models.base import BaseForecaster

logger = logging.getLogger(__name__)


def _default_config(input_length: int, prediction_length: int, num_features: int) -> PatchTSTConfig:
    return PatchTSTConfig(
        prediction_length=prediction_length,
        context_length=input_length,
        patch_length=16,
        stride=8,
        num_input_channels=num_features,
    )


class PatchTSTForecaster(BaseForecaster):
    def __init__(self, config: PatchTSTConfig):
        self.model = PatchTSTForPrediction(config)
        self.config = config

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        # Minimal manual training loop for demo (not optimized)
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        X_tensor = torch.tensor(X, dtype=torch.float32, device=device)
        y_tensor = torch.tensor(y, dtype=torch.float32, device=device)
        for epoch in range(3):
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = torch.nn.functional.mse_loss(outputs.predictions, y_tensor)
            loss.backward()
            optimizer.step()
            logger.info("Epoch %d loss %.4f", epoch + 1, loss.item())

    def predict(self, X: np.ndarray, horizon: int, exog: Any | None = None) -> np.ndarray:
        self.model.eval()
        device = next(self.model.parameters()).device
        X_tensor = torch.tensor(X[-1:], dtype=torch.float32, device=device)
        with torch.no_grad():
            outputs = self.model(X_tensor)
        preds = outputs.predictions.cpu().numpy()[0, :horizon]
        return preds

    def save(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(path)
        logger.info("Saved PatchTST model to %s", path)

    @classmethod
    def load(cls, path: str) -> "PatchTSTForecaster":
        model = PatchTSTForPrediction.from_pretrained(path)
        forecaster = cls(model.config)
        forecaster.model = model
        return forecaster

    @classmethod
    def from_data(cls, X: np.ndarray, horizon: int) -> "PatchTSTForecaster":
        cfg = _default_config(input_length=X.shape[1], prediction_length=horizon, num_features=X.shape[2] if X.ndim == 3 else 1)
        return cls(cfg)
