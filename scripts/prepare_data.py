#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from energy_app.data.loader import load_consumption_csv
from energy_app.data.preprocess import fill_and_resample, time_based_split, SplitConfig
from energy_app.data.features import build_baseline_matrix
from energy_app.data.windows import build_transformer_windows, WindowConfig
from energy_app.logging_utils import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare consumption dataset")
    parser.add_argument("--input", required=True, help="Input CSV with timestamp, consumption")
    parser.add_argument("--output-dir", required=True, help="Output directory for processed data")
    parser.add_argument("--tz", default=None, help="Timezone (e.g., Europe/Budapest)")
    parser.add_argument("--window", type=int, default=168, help="Context window size")
    parser.add_argument("--horizon", type=int, default=24, help="Forecast horizon hours")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_consumption_csv(args.input, tz=args.tz)
    df = fill_and_resample(df, tz=args.tz)
    train, val, test = time_based_split(df, SplitConfig())

    baseline = build_baseline_matrix(df)
    baseline_path = out_dir / "baseline.parquet"
    baseline.to_parquet(baseline_path, index=False)

    window_cfg = WindowConfig(window=args.window, horizon=args.horizon)
    X, y = build_transformer_windows(df, window_cfg)
    npz_path = out_dir / "windows.npz"
    import numpy as np

    np.savez_compressed(npz_path, X=X, y=y)

    # Save splits for later evaluation
    train.to_csv(out_dir / "train.csv", index=False)
    val.to_csv(out_dir / "val.csv", index=False)
    test.to_csv(out_dir / "test.csv", index=False)

    print(f"Baseline features -> {baseline_path}")
    print(f"Transformer windows -> {npz_path}")
    print(f"Splits saved to {out_dir}")


if __name__ == "__main__":
    main()
