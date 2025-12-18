from energy_app.weather.client import OpenMeteoClient, OpenMeteoConfig


def test_cache_key_stable(tmp_path):
    cfg = OpenMeteoConfig(base_url="https://api.open-meteo.com/v1", geocoding_url="https://geocoding-api.open-meteo.com/v1", cache_path=tmp_path / "cache.sqlite")
    client = OpenMeteoClient(cfg)
    key1 = client._cache_key(47.5, 19.1, "2024-01-01", "2024-01-02", ["temperature_2m"], "historical")
    key2 = client._cache_key(47.5, 19.1, "2024-01-01", "2024-01-02", ["temperature_2m"], "historical")
    assert key1 == key2
