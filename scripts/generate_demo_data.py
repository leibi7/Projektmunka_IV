#!/usr/bin/env python
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/sample_consumption.csv")
    ap.add_argument("--days", type=int, default=30)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    start = datetime.utcnow() - timedelta(days=args.days)
    timestamps = pd.date_range(start=start, periods=args.days * 24, freq="H", tz="UTC")
    base = 0.8 + 0.2 * np.sin(np.linspace(0, 10, len(timestamps)))
    noise = np.random.normal(0, 0.05, size=len(timestamps))
    consumption = base + noise
    df = pd.DataFrame({"timestamp": timestamps, "consumption": consumption})
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Demo data saved to {out_path}")


if __name__ == "__main__":
    main()
