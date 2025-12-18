FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

RUN useradd -m appuser
WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appuser ${APP_HOME}
USER appuser

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:7860/health || exit 1

CMD ["python", "-m", "energy_app"]
