FROM python:3.13-slim-bullseye

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY . /app

WORKDIR /app
RUN uv sync --frozen --no-cache


CMD ["./.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]