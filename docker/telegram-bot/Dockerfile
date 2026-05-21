# syntax=docker/dockerfile:1
# ARM64-ready Python image for Raspberry Pi 400
FROM --platform=$TARGETPLATFORM python:3.12-slim

ARG TARGETPLATFORM
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY bot.py /app/bot.py

# Volumes expected from docker-compose:
# - /app/config -> bot settings/secrets files
# - /app/logs   -> bot runtime logs
VOLUME ["/app/config", "/app/logs"]

# No inbound port is required for Telegram polling mode.
# For webhook mode, expose and map your selected port in compose.
CMD ["python", "/app/bot.py"]
