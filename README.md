# Energy Forecasting & Recommendations (Projektmunka IV)

Production-ready, Dockerized Gradio webapp that forecasts household energy consumption with weather context and provides agentic, actionable recommendations.

## Features
- Time-series forecasting with Baseline (LightGBM), PatchTST transformer, and IBM Granite TTM (zero-shot)
- Weather via Open-Meteo (geocoding, historical, forecast) with SQLite caching
- Profile storage (SQLite by default, Supabase adapter-ready)
- Agentic LLM recommendations with deterministic tool-calling flow
- Reproducible data prep, training, evaluation pipelines and plots
- Docker Compose deployment with Caddy reverse proxy + TLS for `leibi.hu`

## Repository Layout
```
config/            # app configuration
src/energy_app/    # package modules
scripts/           # CLI utilities
infra/Caddyfile    # reverse proxy
artifacts/         # model + report outputs (volume in Docker)
data/              # local data/cache (volume in Docker)
```

## Quickstart (local)
1. Install Python 3.11 and `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and set values (at minimum `APP_ENV` and `TZ`).
3. Generate demo data (if you do not have your own): `python scripts/generate_demo_data.py --output data/sample_consumption.csv`.
4. Prepare data (resample, features, splits): `python scripts/prepare_data.py --input data/sample_consumption.csv --output-dir artifacts/processed`.
5. (Optional) Fetch weather for demo location: `python scripts/fetch_weather.py --location "Budapest" --start 2024-01-01 --end 2024-01-07`.
6. Run baseline training: `python scripts/train_baseline.py --data artifacts/processed/baseline.parquet --output artifacts/baseline_model.pkl`.
7. Launch app: `python -m energy_app` then open http://localhost:7860.

## Docker (local)
```
docker compose up -d --build
```
App runs behind Caddy at https://localhost (self-signed unless proper certs).

## Production deploy on VPS (leibi.hu)
- Point DNS A record for `leibi.hu` to server IP.
- Install Docker + Compose: `curl -fsSL https://get.docker.com | sh` (or distro package).
- Place repo on server, set `.env` values, and run `docker compose up -d --build`.
- Ensure firewall only allows 22 (SSH) and 80/443.
- Caddy handles TLS (Let’s Encrypt) automatically. Reverse proxies to app (internal network only). Security headers enabled. BasicAuth snippet available in `infra/Caddyfile` (commented).

## Configuration
- `config/settings.yaml`: default paths and Open-Meteo endpoints.
- Environment overrides: `.env` (see `.env.example`).
- Database: default SQLite at `data/app.db`. Weather cache at `data/weather_cache.sqlite`.

## Testing
```
make test
```
Runs unit tests for data windowing, weather cache keys, and profile CRUD.

## Scripts
- `scripts/prepare_data.py`: ingestion, preprocessing, feature engineering, window export
- `scripts/fetch_weather.py`: geocoding + historical/forecast fetch with caching
- `scripts/train_baseline.py`: train baseline model
- `scripts/train_patchtst.py`: fine-tune PatchTST
- `scripts/eval_models.py`: evaluate multiple models, produce reports
- `scripts/generate_demo_data.py`: synthesize demo consumption CSV

## Notes
- IBM Granite TTM is used in zero-shot mode by default. Fine-tuning hook left experimental.
- Supabase integration is optional; default storage works without it.
- No secrets are committed; use `.env` for keys.
