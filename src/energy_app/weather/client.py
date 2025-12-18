from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlencode

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from energy_app.weather.cache import WeatherCache

logger = logging.getLogger(__name__)


WEATHER_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "precipitation",
    "cloud_cover",
]


@dataclass
class OpenMeteoConfig:
    base_url: str
    geocoding_url: str
    cache_path: str


class OpenMeteoClient:
    def __init__(self, config: OpenMeteoConfig):
        self.cfg = config
        self.cache = WeatherCache(config.cache_path)

    def _cache_key(self, lat: float, lon: float, start: str, end: str, variables: List[str], granularity: str) -> str:
        key = {
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "start": start,
            "end": end,
            "vars": sorted(variables),
            "granularity": granularity,
        }
        return urlencode(key, doseq=True)

    @retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
    def geocode(self, location: str) -> Optional[Dict]:
        params = {"name": location}
        url = f"{self.cfg.geocoding_url}/search"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return results[0] if results else None

    @retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
    def historical(self, lat: float, lon: float, start: str, end: str, hourly: List[str] | None = None) -> Dict:
        variables = hourly or WEATHER_VARS
        key = self._cache_key(lat, lon, start, end, variables, "historical")
        cached = self.cache.get(key)
        if cached:
            logger.info("Weather cache hit for %s", key)
            return cached
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "hourly": ",".join(variables),
            "timezone": "auto",
        }
        url = f"{self.cfg.base_url}/archive"
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        self.cache.set(key, data)
        return data

    @retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
    def forecast(self, lat: float, lon: float, days: int = 3, hourly: List[str] | None = None) -> Dict:
        variables = hourly or WEATHER_VARS
        key = self._cache_key(lat, lon, f"next-{days}", f"next-{days}", variables, "forecast")
        cached = self.cache.get(key)
        if cached:
            logger.info("Weather cache hit for %s", key)
            return cached
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "hourly": ",".join(variables),
            "timezone": "auto",
        }
        url = f"{self.cfg.base_url}/forecast"
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        self.cache.set(key, data)
        return data
