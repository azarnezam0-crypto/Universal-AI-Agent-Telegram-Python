"""OmniAgent — self-hosted Telegram AI agent (entry point)."""
import logging
import os

from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes

from db.session import init_db
from handlers import register_handlers

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

COMMANDS = [
    ("start", "شروع"),
    ("help", "راهنما"),
    ("setapi", "اندپوینت + کلید"),
    ("models", "لیست مدل‌ها"),
    ("setmodel", "انتخاب مدل"),
    ("setsystem", "سیستم‌پرامپت"),
    ("setmemory", "پنجره حافظه"),
    ("tts", "صدا on/off"),
    ("profile", "پروفایل"),
    ("history", "تاریخچه"),
    ("forget", "پاک کردن حافظه"),
    ("newchat", "چت جدید"),
    ("research", "جستجوی عمیق"),
    ("setpref", "تنظیم دلخواه"),
]


async def _post_init(app):
    try:
        await app.bot.set_my_commands([BotCommand(c, d) for c, d in COMMANDS])
    except Exception as e:  # bad token / no network at boot shouldn't kill the bot
        logger.warning("set_my_commands failed (bot still running): %s", e)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set. Get one from @BotFather.")

    init_db()
    logger.info("Database initialized.")

    app = ApplicationBuilder().token(token).post_init(_post_init).build()
    register_handlers(app)
    app.add_error_handler(error_handler)

    logger.info("OmniAgent starting...")
    while True:
        try:
            app.run_polling(
                allowed_updates=["message"],
                bootstrap_retries=10,
                read_timeout=30,
                connect_timeout=30,
                pool_timeout=30,
            )
        except Exception as e:  # transient network error shouldn't crash the process
            logger.error("Polling stopped, restarting in 5s: %s", e, exc_info=True)
            import time
            time.sleep(5)


if __name__ == "__main__":
    main()
