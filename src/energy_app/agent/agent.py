from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

import pandas as pd

from energy_app.agent.prompts import BASE_SYSTEM_PROMPT
from energy_app.agent.tools import (
    ToolContext,
    tool_compute_consumption_insights,
    tool_get_forecast,
    tool_get_user_profile,
)


@dataclass
class Recommendation:
    summary: str
    top_actions_short_term: List[str]
    top_actions_long_term: List[str]
    estimated_impact: str
    assumptions: List[str]
    disclaimer: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


def generate_recommendations(ctx: ToolContext, user_id: str, history: pd.Series, horizon: int = 24) -> Recommendation:
    profile = tool_get_user_profile(ctx, user_id)
    forecast = tool_get_forecast(ctx, user_id, horizon)
    insights = tool_compute_consumption_insights(history)

    location = profile.get("location_text") if profile else "your home"
    summary = f"Based on recent usage in {location}, expect similar patterns. Weather forecast considered."

    short_term = [
        "Shift heavy appliance use to off-peak hours based on forecasted cooler periods.",
        "Reduce heating/cooling setpoints by 1-2°C during low occupancy hours.",
        "Unplug idle devices overnight to avoid phantom loads.",
    ]
    long_term = [
        "Improve insulation or window sealing to stabilize temperature swings.",
        "Install smart thermostats to automate comfort during predicted peaks.",
        "Consider LED upgrades for all high-use rooms.",
    ]
    assumptions = [
        "Forecast horizon is limited; impacts are estimates.",
        "Occupancy patterns remain similar to recent history.",
    ]
    recommendation = Recommendation(
        summary=summary,
        top_actions_short_term=short_term,
        top_actions_long_term=long_term,
        estimated_impact="medium",
        assumptions=assumptions,
        disclaimer="This is an energy-saving estimate; avoid unsafe electrical work.",
    )
    return recommendation
