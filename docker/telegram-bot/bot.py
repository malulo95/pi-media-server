import asyncio
import logging
import os
import signal
from collections import deque
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_ALLOWED_CHAT = os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "")
START_MESSAGE = os.getenv("TELEGRAM_START_MESSAGE", "Bot de Pi Media Server en línea ✅")
STATUS_MESSAGE = os.getenv(
    "TELEGRAM_STATUS_MESSAGE",
    "Servicios docker activos. Revisa docker compose ps en la Pi.",
)
BEETS_LOG_PATH = os.getenv("BEETS_LOG_PATH", "/beets-config/import.log")
BEETS_FAILURES_LIMIT = int(os.getenv("BEETS_FAILURES_LIMIT", "20"))

# Beets log prefixes that mean a file was NOT cleanly matched/imported.
# "skip"         – item was skipped (no match found or ambiguous in quiet mode)
# "asis"         – imported without metadata (no match accepted)
# "duplicate_*"  – a duplicate was detected and handled (skipped or replaced)
_FAILURE_PREFIXES = ("skip ", "asis ", "duplicate_skip ", "duplicate_replace ", "duplicate_merge ")


def _parse_beets_failures(log_path: str, limit: int) -> list[str]:
    """Return the last *limit* lines from the beets import log that represent
    failed or imperfect ingest events (skips, asis, duplicates).

    Uses a deque so only *limit* failure lines are kept in memory at once,
    regardless of total log size.
    """
    path = Path(log_path)
    if not path.exists():
        return []
    # Keep only the last `limit` matches without buffering the whole log.
    window: deque[str] = deque(maxlen=limit)
    with path.open(encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if any(line.startswith(prefix) for prefix in _FAILURE_PREFIXES):
                window.append(line)
    return list(window)


def _safe_truncate(text: str, max_bytes: int = 4090) -> str:
    """Truncate *text* to *max_bytes* UTF-8 bytes without breaking characters."""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore") + "\n…"


def _log_unauthorized(command: str, update: Update) -> None:
    chat = update.effective_chat
    user = update.effective_user
    logging.warning(
        "Unauthorized %s from chat_id=%s chat_title=%s user=%s user_id=%s",
        command,
        getattr(chat, "id", "unknown"),
        getattr(chat, "title", ""),
        getattr(user, "username", ""),
        getattr(user, "id", "unknown"),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        _log_unauthorized("/start", update)
        return
    await update.message.reply_text(START_MESSAGE)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        _log_unauthorized("/status", update)
        return
    await update.message.reply_text(STATUS_MESSAGE)


async def failures(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply with the last N beets import failures (skipped / no-match / asis)."""
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        _log_unauthorized("/failures", update)
        return

    entries = _parse_beets_failures(BEETS_LOG_PATH, BEETS_FAILURES_LIMIT)

    if not entries:
        log_exists = Path(BEETS_LOG_PATH).exists()
        if not log_exists:
            await update.message.reply_text(
                f"⚠️ No se encontró el log de beets en:\n{BEETS_LOG_PATH}\n\n"
                "Asegurate de que el volumen esté montado y de haber corrido una importación."
            )
        else:
            await update.message.reply_text("✅ No hay archivos fallidos ni sin match en el log de beets.")
        return

    lines = "\n".join(f"• {e}" for e in entries)
    header = f"❌ Últimos {len(entries)} archivos fallidos / sin match perfecto en beets:\n\n"
    message = _safe_truncate(header + lines)
    await update.message.reply_text(message)


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is required but not set. "
            "Set it in a .env file or export it before running docker compose up."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("failures", failures))

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await stop_event.wait()
    await app.updater.stop()
    await app.stop()
    await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_ALLOWED_CHAT = os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "")
START_MESSAGE = os.getenv("TELEGRAM_START_MESSAGE", "Bot de Pi Media Server en línea ✅")
STATUS_MESSAGE = os.getenv(
    "TELEGRAM_STATUS_MESSAGE",
    "Servicios docker activos. Revisa docker compose ps en la Pi.",
)
BEETS_LOG_PATH = os.getenv("BEETS_LOG_PATH", "/beets-config/import.log")
BEETS_FAILURES_LIMIT = int(os.getenv("BEETS_FAILURES_LIMIT", "20"))

# Beets log prefixes that mean a file was NOT cleanly matched/imported.
# "skip"         – item was skipped (no match found or ambiguous in quiet mode)
# "asis"         – imported without metadata (no match accepted)
# "duplicate_*"  – a duplicate was detected and handled (skipped or replaced)
_FAILURE_PREFIXES = ("skip ", "asis ", "duplicate_skip ", "duplicate_replace ", "duplicate_merge ")


def _parse_beets_failures(log_path: str, limit: int) -> list[str]:
    """Return the last *limit* lines from the beets import log that represent
    failed or imperfect ingest events (skips, asis, duplicates)."""
    path = Path(log_path)
    if not path.exists():
        return []
    failures: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if any(line.lower().startswith(prefix) for prefix in _FAILURE_PREFIXES):
                failures.append(line)
    return failures[-limit:]


def _log_unauthorized(command: str, update: Update) -> None:
    chat = update.effective_chat
    user = update.effective_user
    logging.warning(
        "Unauthorized %s from chat_id=%s chat_title=%s user=%s user_id=%s",
        command,
        getattr(chat, "id", "unknown"),
        getattr(chat, "title", ""),
        getattr(user, "username", ""),
        getattr(user, "id", "unknown"),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        _log_unauthorized("/start", update)
        return
    await update.message.reply_text(START_MESSAGE)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        _log_unauthorized("/status", update)
        return
    await update.message.reply_text(STATUS_MESSAGE)


async def failures(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply with the last N beets import failures (skipped / no-match / asis)."""
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        _log_unauthorized("/failures", update)
        return

    entries = _parse_beets_failures(BEETS_LOG_PATH, BEETS_FAILURES_LIMIT)

    if not entries:
        log_exists = Path(BEETS_LOG_PATH).exists()
        if not log_exists:
            await update.message.reply_text(
                f"⚠️ No se encontró el log de beets en:\n{BEETS_LOG_PATH}\n\n"
                "Asegurate de que el volumen esté montado y de haber corrido una importación."
            )
        else:
            await update.message.reply_text("✅ No hay archivos fallidos ni sin match en el log de beets.")
        return

    lines = "\n".join(f"• {e}" for e in entries)
    header = f"❌ Últimos {len(entries)} archivos fallidos / sin match perfecto en beets:\n\n"
    # Telegram message limit is 4096 chars; truncate if needed.
    message = header + lines
    if len(message) > 4096:
        message = message[:4090] + "\n…"
    await update.message.reply_text(message)


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is required but not set. "
            "Set it in a .env file or export it before running docker compose up."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("failures", failures))

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await stop_event.wait()
    await app.updater.stop()
    await app.stop()
    await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
