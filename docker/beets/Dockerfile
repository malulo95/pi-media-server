# syntax=docker/dockerfile:1
# ARM64-ready image for Raspberry Pi 400 (linux/arm64)
FROM --platform=$TARGETPLATFORM python:3.12-slim

ARG TARGETPLATFORM
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Runtime deps used by beets plugins (acoustid/chromaprint, ffmpeg)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        chromaprint-tools \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# beets + common plugins for music organization
RUN pip install --no-cache-dir \
    beets \
    pyacoustid \
    requests

WORKDIR /workspace

# Volumes expected from docker-compose:
# - /config  -> beets config + database
# - /library -> organized music library (FLAC/otros)
# - /imports -> incoming downloads to import
VOLUME ["/config", "/library", "/imports"]

# Keep container running as a utility service for ARM home servers.
# Example usage:
#   docker compose exec beets beet -c /config/config.yaml import /imports
CMD ["tail", "-f", "/dev/null"]
