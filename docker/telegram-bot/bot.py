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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        logging.warning("Unauthorized /start request from chat_id=%s", update.effective_chat.id)
        return
    await update.message.reply_text("Bot de Pi Media Server en línea ✅")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        logging.warning("Unauthorized /status request from chat_id=%s", update.effective_chat.id)
        return
    await update.message.reply_text("Servicios docker activos. Revisa docker compose ps en la Pi.")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")

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
