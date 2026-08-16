"""OmniAgent — self-hosted Telegram AI agent (entry point)."""
import asyncio
import logging
import os
import time
import traceback

from dotenv import load_dotenv
from telegram import Bot, BotCommand
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


def _admin_ids():
    return {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}


async def _post_init(app):
    try:
        await app.bot.set_my_commands([BotCommand(c, d) for c, d in COMMANDS])
    except Exception as e:  # bad token / no network at boot shouldn't kill the bot
        logger.warning("set_my_commands failed (bot still running): %s", e)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    text = f"❌ خطا:\n{type(context.error).__name__}: {context.error}"
    for aid in _admin_ids():
        try:
            await context.application.bot.send_message(aid, text[:4000])
        except Exception:
            pass


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set. Get one from @BotFather.")

    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error("init_db failed (bot will still start, but DB calls will error): %s", e, exc_info=True)

    logger.info("OmniAgent starting...")
    while True:
        app = ApplicationBuilder().token(token).post_init(_post_init).build()
        register_handlers(app)
        app.add_error_handler(error_handler)
        try:
            app.run_polling(
                allowed_updates=["message"],
                bootstrap_retries=10,
                read_timeout=30,
                connect_timeout=30,
                pool_timeout=30,
            )
            break  # clean exit
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # transient network error shouldn't crash the process
            logger.error("Polling stopped, restarting in 5s: %s", e, exc_info=True)
            # surface fatal polling errors to admins via a direct API call
            try:
                b = Bot(token)
                tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                loop = asyncio.new_event_loop()
                for aid in _admin_ids():
                    try:
                        loop.run_until_complete(b.send_message(aid, f"❌ Polling crash:\n{tb[-3500:]}"))
                    except Exception:
                        pass
                loop.close()
            except Exception:
                pass
            time.sleep(5)


if __name__ == "__main__":
    main()
