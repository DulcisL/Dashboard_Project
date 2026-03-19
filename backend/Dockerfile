# Backend: Django + DRF
FROM python:3.12-slim

# Prevent Python from writing .pyc and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# System deps: build tools + Postgres client libs + compression libs
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  curl \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app

# Expose Django/Gunicorn port
EXPOSE 8000

# Local-friendly default; docker-compose can override this.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
