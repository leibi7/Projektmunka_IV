from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

from energy_app.storage.profile_repo import ProfileRepository
from energy_app.weather.client import OpenMeteoClient
from energy_app.weather.features import weather_to_frame


@dataclass
class ToolContext:
    profile_repo: ProfileRepository
    weather_client: OpenMeteoClient


def tool_get_user_profile(ctx: ToolContext, user_id: str) -> Dict[str, Any] | None:
    profile = ctx.profile_repo.get_profile(user_id)
    return profile.__dict__ if profile else None


def tool_get_forecast(ctx: ToolContext, user_id: str, horizon: int) -> Dict[str, Any]:
    profile = ctx.profile_repo.get_profile(user_id)
    if not profile:
        raise ValueError("No profile for user")
    forecast = ctx.weather_client.forecast(profile.lat, profile.lon, days=max(1, horizon // 24))
    return forecast


def tool_get_weather_summary(ctx: ToolContext, lat: float, lon: float, horizon: int) -> pd.DataFrame:
    payload = ctx.weather_client.forecast(lat, lon, days=max(1, horizon // 24))
    df = weather_to_frame(payload)
    return df.head(horizon)


def tool_compute_consumption_insights(timeseries: pd.Series) -> Dict[str, Any]:
    rolling = timeseries.rolling(window=24, min_periods=1)
    summary = {
        "peak_hour": int(timeseries.idxmax()) if len(timeseries) else None,
        "mean": float(timeseries.mean()) if len(timeseries) else None,
        "std": float(timeseries.std()) if len(timeseries) else None,
        "rolling_mean": rolling.mean().tolist(),
    }
    return summary
