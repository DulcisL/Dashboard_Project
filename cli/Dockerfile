FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

COPY . /app

# Default to idle so you can exec in and run obs.py
CMD ["tail", "-f", "/dev/null"]
