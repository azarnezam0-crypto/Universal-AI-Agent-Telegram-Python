"""History / memory / preference handlers for OmniAgent."""
from telegram import Update
from telegram.ext import ContextTypes

from db.session import SessionLocal
from services.memory_service import MemoryService

memory = MemoryService()


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        rows = memory.get_history(db, user, limit=10)
        if not rows:
            await update.message.reply_text("تاریخچه‌ای نیست.")
            return
        text = "\n\n".join(f"{m['role']}: {m['content']}" for m in rows)
        await update.message.reply_text(text[:4000])
    finally:
        db.close()


async def cmd_forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        memory.clear_history(db, user)
        await update.message.reply_text("✅ حافظه پاک شد (پروفایل می‌مونه).")
    finally:
        db.close()


async def cmd_setpref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setpref <key> <value>")
        return
    key = context.args[0]
    value = " ".join(context.args[1:])
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        memory.set_preference(db, user, key, value)
        await update.message.reply_text(f"✅ {key} = {value}")
    finally:
        db.close()
