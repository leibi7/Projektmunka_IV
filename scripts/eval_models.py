#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from energy_app.logging_utils import configure_logging
from energy_app.models.baseline import BaselineForecaster
from energy_app.eval.evaluator import evaluate_models
from energy_app.eval.reporting import save_markdown_report, plot_predictions, plot_residuals


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="CSV test split")
    ap.add_argument("--baseline-model", default="artifacts/baseline_model.pkl")
    ap.add_argument("--output", default="artifacts/reports")
    ap.add_argument("--horizon", type=int, default=24)
    return ap.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    df = pd.read_csv(args.data)
    baseline = BaselineForecaster.load(args.baseline_model)

    metrics_df = evaluate_models([
        ("baseline", baseline),
    ], df, args.horizon, args.output)

    metrics_md = Path(args.output) / "metrics.md"
    save_markdown_report(metrics_df, metrics_md)

    y_true = df["consumption"].tail(args.horizon).reset_index(drop=True)
    preds = {
        "baseline": pd.Series(baseline.predict(df, args.horizon)),
    }
    plot_predictions(y_true, preds, args.output)
    plot_residuals(y_true, preds, args.output)

    print(f"Reports saved to {args.output}")


if __name__ == "__main__":
    main()
