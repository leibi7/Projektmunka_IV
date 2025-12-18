from __future__ import annotations

import logging
from pathlib import Path

import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd

from energy_app.config import load_config
from energy_app.logging_utils import configure_logging
from energy_app.storage.db import Database
from energy_app.storage.profile_repo import Profile, ProfileRepository
from energy_app.weather.client import OpenMeteoClient, OpenMeteoConfig
from energy_app.agent.agent import generate_recommendations
from energy_app.agent.tools import ToolContext
from energy_app.webapp.ui import build_interface
from energy_app.models.baseline import BaselineForecaster

logger = logging.getLogger(__name__)


def create_app():
    configure_logging()
    cfg = load_config()
    db = Database(cfg.get("db_url", "sqlite:///data/app.db"))
    repo = ProfileRepository(db)
    weather_client = OpenMeteoClient(
        OpenMeteoConfig(
            base_url=cfg["open_meteo"]["base_url"],
            geocoding_url=cfg["open_meteo"]["geocoding_url"],
            cache_path=cfg["weather_cache"],
        )
    )
    tool_ctx = ToolContext(profile_repo=repo, weather_client=weather_client)

    baseline_path = cfg["models"]["baseline_path"]
    baseline_model = BaselineForecaster.load(baseline_path) if Path(baseline_path).exists() else BaselineForecaster()

    def run_save_profile(user_id: str, location: str, area: float, occupants: int, heating: str):
        # geocode for lat/lon
        geo = weather_client.geocode(location) if location else None
        lat = geo.get("latitude") if geo else 0.0
        lon = geo.get("longitude") if geo else 0.0
        profile = Profile(
            user_id=user_id,
            location_text=location or "",
            lat=lat,
            lon=lon,
            area_m2=area or 0,
            occupants=int(occupants or 0),
            heating_type=heating or None,
        )
        repo.upsert_user(user_id)
        repo.upsert_profile(profile)
        return f"Profile saved for {user_id} ({location})"

    def run_forecast(user_id: str, horizon: int, model_name: str):
        # Use baseline history from sample data
        data_path = cfg.get("data_path")
        if not Path(data_path).exists():
            raise gr.Error("No data file found. Generate demo data first.")
        df = pd.read_csv(data_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        history = df.tail(200)
        preds = baseline_model.predict(history, horizon)
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(history["timestamp"].tail(50), history["consumption"].tail(50), label="History")
        future_index = pd.date_range(history["timestamp"].iloc[-1], periods=horizon + 1, freq="H")[1:]
        ax.plot(future_index, preds, label=f"Prediction ({model_name})")
        ax.legend()
        ax.set_title("Forecast")
        fig.autofmt_xdate()
        return fig

    def run_recommendations(user_id: str):
        data_path = cfg.get("data_path")
        df = pd.read_csv(data_path)
        recs = generate_recommendations(tool_ctx, user_id, df["consumption"].tail(168))
        return recs.__dict__

    demo = build_interface(run_save_profile, run_forecast, run_recommendations)

    @demo.app.get(\"/health\")  # type: ignore[attr-defined]
    def _healthcheck():  # pragma: no cover - simple liveness
        return {\"status\": \"ok\"}

    return demo


def main():
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860, show_api=False)


if __name__ == "__main__":
    main()
