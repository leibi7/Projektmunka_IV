from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from energy_app.models.metrics import evaluate_series

logger = logging.getLogger(__name__)


def evaluate_models(models: List[Tuple[str, object]], df: pd.DataFrame, horizon: int, output_dir: str) -> pd.DataFrame:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = []
    y_true = df["consumption"].tail(horizon).reset_index(drop=True)
    for name, model in models:
        try:
            preds = model.predict(df, horizon) if hasattr(model, "predict") else np.zeros_like(y_true)
            preds_series = pd.Series(preds).reset_index(drop=True)
            metrics = evaluate_series(y_true, preds_series)
            metrics["model"] = name
            results.append(metrics)
            logger.info("Evaluated %s", name)
        except Exception as exc:  # pragma: no cover - guardrail
            logger.exception("Evaluation failed for %s: %s", name, exc)
    metrics_df = pd.DataFrame(results)
    metrics_path = Path(output_dir) / "metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)
    return metrics_df
