"""History / memory / preference handlers for OmniAgent."""
from telegram import Update
from telegram.ext import ContextTypes

from db.session import SessionLocal
from services.memory_service import MemoryService
from services.message_utils import split_message

memory = MemoryService()


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        sess = memory.get_current_session(db, user)
        rows = memory.get_history(db, user, limit=10)
        if not rows:
            await update.message.reply_text(f"تاریخچه‌ای در سشن #{sess.id} نیست.")
            return
        text = "\n\n".join(f"{m['role']}: {m['content']}" for m in rows)
        for part in split_message(text):
            await update.message.reply_text(part)
    finally:
        db.close()


async def cmd_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        sessions = memory.list_sessions(db, user)
        if not sessions:
            await update.message.reply_text("هیچ سشنی نیست.")
            return
        lines = []
        for s in sessions:
            mark = " ✅" if s.id == user.current_session_id else ""
            lines.append(f"#{s.id}{mark} — {s.message_count} پیام — {s.started_at}")
        await update.message.reply_text("سشن‌ها:\n" + "\n".join(lines))
    finally:
        db.close()


async def cmd_newchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        old = user.current_session_id
        sess = memory.new_session(db, user)
        await update.message.reply_text(f"✅ سشن جدید #{sess.id} ساخته شد (سشن قبلی #{old} محفوظه).")
    finally:
        db.close()


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /resume <session_id>")
        return
    sid = int(context.args[0])
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        sess = memory.resume_session(db, user, sid)
        if sess:
            await update.message.reply_text(f"✅ رفتی به سشن #{sess.id}.")
        else:
            await update.message.reply_text("⛔ اون سشن متعلق به تو نیست یا وجود ندارد.")
    finally:
        db.close()


async def cmd_forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        sess = memory.get_current_session(db, user)
        memory.clear_session(db, user, sess)
        await update.message.reply_text(f"✅ سشن فعلی #{sess.id} پاک شد (بقیه سشن‌ها می‌مونن).")
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
