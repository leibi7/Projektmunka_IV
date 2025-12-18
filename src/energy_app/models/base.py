from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class BaseForecaster(ABC):
    @abstractmethod
    def fit(self, X: Any, y: Any) -> None:
        ...

    @abstractmethod
    def predict(self, X: Any, horizon: int, exog: Any | None = None) -> Any:
        ...

    @abstractmethod
    def save(self, path: str) -> None:
        ...

    @classmethod
    @abstractmethod
    def load(cls, path: str) -> "BaseForecaster":
        ...


class PredictContext:
    def __init__(self, history: pd.DataFrame):
        self.history = history
