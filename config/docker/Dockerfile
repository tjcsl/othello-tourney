FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    postgresql-client \
    firejail \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000