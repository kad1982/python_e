FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# системные зависимости (asyncpg — чистый Python, libpq не нужна)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# сначала зависимости — используем кэш слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# затем исходники
COPY app/ ./app/
COPY settings/ ./settings/

# точка входа
CMD ["python", "-m", "app.main"]