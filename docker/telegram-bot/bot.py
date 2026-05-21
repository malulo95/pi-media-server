import asyncio
import logging
import os
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
        return
    await update.message.reply_text("Pi Media Server bot online ✅")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if BOT_ALLOWED_CHAT and str(update.effective_chat.id) != BOT_ALLOWED_CHAT:
        return
    await update.message.reply_text("Servicios docker activos. Revisa docker compose ps en la Pi.")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
