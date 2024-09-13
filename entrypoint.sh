#!/bin/bash
echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Starting FastAPI..."
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080