FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=2

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates tini && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM base AS runtime
RUN useradd -u 10001 -m appuser
USER appuser
WORKDIR /app
COPY . .
ENV ENV=prod LOG_LEVEL=info HOST=0.0.0.0 PORT=8080
ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["bash","-lc","alembic upgrade head && python -m uvicorn geoobra_backend_v3.app.main:app --host ${HOST} --port ${PORT}"]
