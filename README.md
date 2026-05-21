# pi-media-server

Stack Docker para Raspberry Pi 400 (ARM64) con:

- `slskd` (Soulseek Daemon)
- `beets` (organización de música)
- `qbittorrent` (`linuxserver/qbittorrent`, multiarch)
- `telegram-bot` (scripts Python)

## Uso rápido

```bash
git clone <repo-url>
cd pi-media-server
cp docker/beets/config.yaml.example data/beets/config/config.yaml
# Exporta token del bot (opcional si no levantas telegram-bot)
export TELEGRAM_BOT_TOKEN="tu_token"
docker compose up -d
```

## Notas

- `docker-compose.yml` usa `platform: linux/arm64` para Pi 400.
- Los Dockerfiles y ejemplos viven en `/docker`.
- No se incluye Jellyfin en Docker (intencional).
