#!/usr/bin/env python
from __future__ import annotations

import argparse

import pandas as pd

from energy_app.logging_utils import configure_logging
from energy_app.models.baseline import BaselineForecaster


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Baseline parquet file")
    ap.add_argument("--output", default="artifacts/baseline_model.pkl")
    return ap.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    df = pd.read_parquet(args.data)
    model = BaselineForecaster()
    X, y = model.build_training_matrix(df)
    model.fit(X, y)
    model.save(args.output)
    print(f"Saved baseline model to {args.output}")


if __name__ == "__main__":
    main()
