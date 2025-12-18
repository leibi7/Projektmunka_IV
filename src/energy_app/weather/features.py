from __future__ import annotations

import pandas as pd
from typing import Dict


def weather_to_frame(payload: Dict) -> pd.DataFrame:
    hourly = payload.get("hourly", {})
    times = pd.to_datetime(hourly.get("time", []))
    data = {k: v for k, v in hourly.items() if k != "time"}
    df = pd.DataFrame(data)
    df.insert(0, "timestamp", times)
    return df


def merge_weather(consumption_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge_asof(
        consumption_df.sort_values("timestamp"),
        weather_df.sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta("1H"),
    )
    return merged
