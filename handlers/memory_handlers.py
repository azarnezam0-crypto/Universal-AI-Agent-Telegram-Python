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
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setpref <key> <value>  (یا /setpref <key> برای حذف)")
        return
    key = context.args[0]
    # single-arg form -> delete that preference
    if len(context.args) == 1:
        db = SessionLocal()
        try:
            user = memory.get_or_create_user(db, update.effective_user.id)
            if memory.delete_preference(db, user, key):
                await update.message.reply_text(f"✅ preference «{key}» پاک شد.")
            else:
                await update.message.reply_text(f"⚠️ preference «{key}» پیدا نشد.")
        finally:
            db.close()
        return
    value = " ".join(context.args[1:])
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        memory.set_preference(db, user, key, value)
        await update.message.reply_text(f"✅ {key} = {value}")
    finally:
        db.close()


async def cmd_clearprefs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        n = memory.clear_preferences(db, user)
        await update.message.reply_text(f"✅ {n} preference پاک شد.")
    finally:
        db.close()


async def cmd_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Skill = تکه‌پرامپت / پرسونای ذخیره‌شده که لایو به چت اضافه می‌شه.\n"
            "/skill add <name> | <instructions...>  - ذخیره اسکیل\n"
            "/skill list  - لیست اسکیل‌ها (✅ = فعال)\n"
            "/skill use <name>  - فعال‌سازی\n"
            "/skill del <name>  - حذف"
        )
        return
    sub = context.args[0].lower()
    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        if sub == "list":
            skills = memory.list_skills(db, user)
            if not skills:
                await update.message.reply_text(
                    "هیچ skillی نداری. بساز:\n/skill add <name> | <دستورالعمل>"
                )
                return
            active = memory.get_preference(db, user, "active_skill")
            lines = [f"🧠 Skillها ({len(skills)}):"]
            for s in skills:
                mark = " ✅" if s.name == active else ""
                lines.append(f"• {s.name}{mark}")
            await update.message.reply_text("\n".join(lines))
            return
        if sub == "add":
            rest = " ".join(context.args[1:])
            if "|" not in rest:
                await update.message.reply_text("فرمت: /skill add <name> | <دستورالعمل>")
                return
            name, _, instructions = rest.partition("|")
            name = name.strip()
            instructions = instructions.strip()
            if not name or not instructions:
                await update.message.reply_text("نام و دستورالعمل هر دو لازمه.")
                return
            memory.add_skill(db, user, name, instructions)
            await update.message.reply_text(
                f"✅ Skill «{name}» ذخیره شد. با /skill use {name} فعالش کن."
            )
            return
        if sub == "use":
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /skill use <name>")
                return
            name = context.args[1].strip()
            if not memory.get_skill(db, user, name):
                await update.message.reply_text(f"⛔ Skill «{name}» وجود ندارد.")
                return
            memory.set_preference(db, user, "active_skill", name)
            await update.message.reply_text(
                f"✅ Skill «{name}» فعال شد و به سیستم‌پرامپت هر پیام اضافه می‌شه."
            )
            return
        if sub == "del":
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /skill del <name>")
                return
            name = context.args[1].strip()
            if memory.delete_skill(db, user, name):
                if memory.get_preference(db, user, "active_skill") == name:
                    memory.delete_preference(db, user, "active_skill")
                await update.message.reply_text(f"✅ Skill «{name}» حذف شد.")
            else:
                await update.message.reply_text(f"⛔ Skill «{name}» پیدا نشد.")
            return
        await update.message.reply_text("زیر‌دستور ناشناخته. بدون آرگومان بزن: /skill")
    finally:
        db.close()
