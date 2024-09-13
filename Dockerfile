FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
