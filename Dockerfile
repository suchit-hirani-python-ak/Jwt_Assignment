FROM python:3.13-slim

# Force Python to show print statements in Docker logs immediately
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Pre-create data directory for SQLite persistence
RUN mkdir -p /app/data

RUN pip install uv
RUN uv sync

EXPOSE 8000

# Now just run the Python app directly
CMD ["uv", "run", "run.py", "--host", "0.0.0.0", "--port", "8000"]
