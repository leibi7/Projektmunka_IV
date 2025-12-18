#!/usr/bin/env python
from __future__ import annotations

import argparse
import numpy as np

from energy_app.logging_utils import configure_logging
from energy_app.models.patchtst import PatchTSTForecaster


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", required=True, help="NPZ file with X, y")
    ap.add_argument("--output", default="artifacts/patchtst")
    ap.add_argument("--horizon", type=int, default=24)
    return ap.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    data = np.load(args.windows)
    X, y = data["X"], data["y"]
    model = PatchTSTForecaster.from_data(X, args.horizon)
    model.fit(X, y)
    model.save(args.output)
    print(f"Saved PatchTST model to {args.output}")


if __name__ == "__main__":
    main()
