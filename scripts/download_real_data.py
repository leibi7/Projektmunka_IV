#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import io
import zipfile

import pandas as pd

# UCI household power consumption dataset (minute-level) via ZIP.
DEFAULT_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip"


def parse_args():
    ap = argparse.ArgumentParser(description="Download real household power consumption dataset sample (UCI).")
    ap.add_argument("--url", default=DEFAULT_URL, help="ZIP URL containing household_power_consumption.txt")
    ap.add_argument("--days", type=int, default=14, help="Number of days to read from the start (minutes = days*24*60)")
    ap.add_argument("--output", default="data/household_power_sample.csv", help="Output CSV path")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    nrows = args.days * 24 * 60 if args.days > 0 else None
    # Download zip into memory to avoid persisting raw.
    import urllib.request

    with urllib.request.urlopen(args.url) as resp:
        zip_bytes = resp.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        with zf.open("household_power_consumption.txt") as f:
            df_raw = pd.read_csv(
                f,
                sep=";",
                na_values=["?"],
                nrows=nrows,
                usecols=["Date", "Time", "Global_active_power"],
            )
    ts = pd.to_datetime(df_raw["Date"] + " " + df_raw["Time"], format="%d/%m/%Y %H:%M:%S", utc=True)
    df = pd.DataFrame(
        {
            "timestamp": ts,
            "consumption": pd.to_numeric(df_raw["Global_active_power"], errors="coerce"),
        }
    ).dropna()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved real dataset sample to {out_path} with {len(df)} rows")


if __name__ == "__main__":
    main()
