FROM python:3.13-slim

# Force Python to show print statements in Docker logs immediately
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libffi-dev \
       redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Pre-create data directory for SQLite/Redis persistence
RUN mkdir -p /app/data

RUN pip install uv
RUN uv sync

EXPOSE 8000

# CHANGED: 
# 1. Removed --save '' so Redis CAN save data.
# 2. Added --dir /app/data so Redis saves to the persistent volume.
CMD ["sh", "-c", "redis-server --daemonize yes --dir /app/data --dbfilename dump.rdb --save 60 1 && exec uv run run.py --host 0.0.0.0 --port 8000"]
