#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from energy_app.config import load_config
from energy_app.logging_utils import configure_logging
from energy_app.weather.client import OpenMeteoClient, OpenMeteoConfig
from energy_app.weather.features import weather_to_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch weather data via Open-Meteo")
    parser.add_argument("--location", required=True, help="City or postcode")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--days", type=int, default=3, help="Forecast days")
    parser.add_argument("--output", default="artifacts/weather.csv", help="Output CSV for historical")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    cfg = load_config()
    client = OpenMeteoClient(
        OpenMeteoConfig(
            base_url=cfg["open_meteo"]["base_url"],
            geocoding_url=cfg["open_meteo"]["geocoding_url"],
            cache_path=cfg["weather_cache"],
        )
    )

    geo = client.geocode(args.location)
    if not geo:
        raise SystemExit("Location not found")

    lat, lon = geo["latitude"], geo["longitude"]
    hist = client.historical(lat, lon, args.start, args.end)
    forecast = client.forecast(lat, lon, args.days)

    df_hist = weather_to_frame(hist)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_hist.to_csv(out_path, index=False)

    print(f"Historical saved to {out_path}")
    print(f"Forecast sample keys: {list(forecast.keys())}")


if __name__ == "__main__":
    main()
