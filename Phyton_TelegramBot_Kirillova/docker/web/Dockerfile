FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# исходники Django-проекта
COPY manage.py ./
COPY django_app/ ./django_app/
COPY events/ ./events/
COPY appointment/ ./appointment/
COPY bot_statistic/ ./bot_statistic/
COPY app/ ./app/
COPY settings/ ./settings/

EXPOSE 8000

# миграции + запуск сервера
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]