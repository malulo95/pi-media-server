import asyncio
import logging
import os
import signal
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


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is required but not set. "
            "Set it in a .env file or export it before running docker compose up."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

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
