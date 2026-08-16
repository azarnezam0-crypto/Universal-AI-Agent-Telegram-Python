"""Core chat + setup handlers for OmniAgent."""
import asyncio
import logging
import os

from telegram import Update
from telegram.ext import ContextTypes

from db.session import SessionLocal

logger = logging.getLogger(__name__)
from services.llm_client import encrypt_key, fetch_models, chat_completion, DEFAULT_SYSTEM_PROMPT, run_agentic, rank_models, probe_model
from services.memory_service import MemoryService
from services.message_utils import split_message
from services.tts_service import text_to_speech
from services.tools import TOOL_DEFINITIONS, TOOL_REGISTRY

memory = MemoryService()


def _admin_ids():
    return {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}


def _db():
    return SessionLocal()


def _agentic_reply(user, messages: list[dict]) -> str:
    """Run an agentic chat turn. Falls back to plain chat if tool-use is
    disabled or the model/endpoint doesn't support function calling."""
    if os.getenv("AGENTIC_TOOLS", "true").lower() == "false":
        return chat_completion(user, messages)
    try:
        return run_agentic(user, messages, TOOL_DEFINITIONS, TOOL_REGISTRY)
    except Exception as e:
        logger.warning("agentic tool-call failed, falling back to plain chat: %s", e)
        return chat_completion(user, messages)


async def _ensure_model(db, user) -> None:
    """Auto-pick a usable chat model on first use so the user never has to
    /setmodel manually. Tries ranked candidates (env DEFAULT_MODEL first, if it
    actually exists in the list) with a real probe call and keeps the first that
    works. A DEFAULT_MODEL with no credentials is skipped, not forced."""
    if user.active_model:
        return
    try:
        models = await asyncio.to_thread(fetch_models, user)
        if not models:
            return
        ranked = rank_models(models)
        default = os.getenv("DEFAULT_MODEL")
        if default and default in models:
            ranked = [default] + ranked
        for candidate in ranked[:8]:
            try:
                await asyncio.to_thread(probe_model, user, candidate)
                user.active_model = candidate
                db.commit()
                logger.info("auto-selected model %s for user %s", candidate, user.telegram_id)
                return
            except Exception as e:
                logger.warning("model %s not usable, trying next: %s", candidate, e)
        logger.warning("no usable model auto-selected for user %s", user.telegram_id)
    except Exception as e:
        logger.warning("auto model selection failed for %s: %s", user.telegram_id, e)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = _db()
    try:
        memory.get_or_create_user(
            db, update.effective_user.id, update.effective_user.username, update.effective_user.full_name
        )
        await update.message.reply_text(
            "👋 سلام! من OmniAgent‌ـم.\n"
            "۱) با /setapi <base_url> <api_key> اندپوینتت رو تنظیم کن\n"
            "۲) با /models لیست مدل‌های اندپوینت رو ببین\n"
            "۳) با /setmodel مدلت رو انتخاب کن\n"
            "بعد هرچی خواستی بپرس. با /help لیست کامل دستورات."
        )
    finally:
        db.close()


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - شروع\n"
        "/setapi <base_url> <api_key> - تنظیم اندپوینت و کلید\n"
        "/models - لیست مدل‌های اندپوینت\n"
        "/setmodel <name> - انتخاب مدل (auto = انتخاب خودکار)\n"
        "/setsystem <prompt> - تنظیم سیستم‌پرامپت (reset = پیش‌فرض)\n"
        "/setmemory <n> - تعداد پیام‌های حافظه\n"
        "/tts on|off - صدای خروجی\n"
        "/profile - پروفایل\n"
        "/history - تاریخچه سشن فعلی\n"
        "/sessions - لیست سشن‌ها\n"
        "/newchat - شروع سشن جدید (قبلی محفوظ)\n"
        "/resume <id> - بازگشت به سشن قبلی\n"
        "/forget - پاک کردن سشن فعلی\n"
        "/research <topic> - جستجوی عمیق\n"
        "/image <prompt> - ساخت عکس (مدل: DEFAULT_IMAGE_MODEL)\n"
        "/web <query> - جستجوی وب\n"
        "/fetch <url> - خواندن محتوای صفحه\n"
        "/setpref <k> <v> - تنظیم دلخواه (فقط <k> = حذف)\n"
        "/clearprefs - پاک کردن همهٔ preferenceها\n"
        "💡 در چت معمولی هم بات خودش برای جستجو/خواندن صفحه از وب استفاده می‌کند."
    )


async def cmd_setapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setapi <base_url> <api_key>")
        return
    base_url, api_key = context.args[0], context.args[1]
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        user.base_url = base_url
        user.api_key_encrypted = encrypt_key(api_key)
        db.commit()
        await update.message.reply_text("✅ اندپوینت و کلید ذخیره شد (رمزنگاری‌شده).")
    finally:
        db.close()


async def cmd_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        try:
            models = await asyncio.to_thread(fetch_models, user)
        except Exception as e:
            await update.message.reply_text(f"⚠️ نتونستم مدل‌ها رو بگیرم: {e}")
            return
        if not models:
            await update.message.reply_text("هیچ مدلی پیدا نشد. اندپوینت/کلید رو چک کن.")
            return
        current = user.active_model or os.getenv("DEFAULT_MODEL", "(تنظیم نشده)")
        text = f"مدل فعلی: {current}\n\nمدل‌های موجود:\n" + "\n".join(models)
        for part in split_message(text):
            await update.message.reply_text(part)
    finally:
        db.close()


async def cmd_setmodel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setmodel <model_name>  (یا /setmodel auto برای انتخاب خودکار)")
        return
    if context.args[0].lower() in {"auto", "reset", "-"}:
        db = _db()
        try:
            user = memory.get_or_create_user(db, update.effective_user.id)
            user.active_model = None
            db.commit()
            await update.message.reply_text("✅ مدل پاک شد؛ روی اولین پیام بات خودش یکی رو انتخاب می‌کند (با تست).")
        finally:
            db.close()
        return
    model = " ".join(context.args)
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        user.active_model = model
        db.commit()
        await update.message.reply_text(f"✅ مدل تنظیم شد: {model}")
    finally:
        db.close()


async def cmd_setsystem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setsystem <prompt text>  (یا /setsystem reset برای بازگشت به پیش‌فرض)")
        return
    if context.args[0].lower() in {"reset", "default", "-"}:
        db = _db()
        try:
            user = memory.get_or_create_user(db, update.effective_user.id)
            user.system_prompt = None
            db.commit()
            await update.message.reply_text("✅ سیستم‌پرامپت به پیش‌فرض (DEFAULT_SYSTEM_PROMPT) برگشت.")
        finally:
            db.close()
        return
    prompt = " ".join(context.args)
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        user.system_prompt = prompt
        db.commit()
        await update.message.reply_text("✅ سیستم‌پرامپت تنظیم شد.")
    finally:
        db.close()


async def cmd_setmemory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /setmemory <n>")
        return
    n = int(context.args[0])
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        user.memory_window = n
        db.commit()
        await update.message.reply_text(f"✅ پنجره‌ی حافظه = {n} پیام.")
    finally:
        db.close()


async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /tts on|off")
        return
    val = context.args[0].lower()
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        user.tts_enabled = (val == "on")
        db.commit()
        await update.message.reply_text(f"✅ TTS = {'روشن' if user.tts_enabled else 'خاموش'}")
    finally:
        db.close()


async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        prefs = memory.get_all_preferences(db, user)
        lines = [
            f"telegram_id: {user.telegram_id}",
            f"base_url: {user.base_url or '(پیش‌فرض)'}" ,
            f"active_model: {user.active_model or '(پیش‌فرض)'}",
            f"tts: {'روشن' if user.tts_enabled else 'خاموش'} ({user.tts_voice})",
            f"memory_window: {user.memory_window}",
            f"system_prompt: {user.system_prompt[:200] if user.system_prompt else '(پیش‌فرض)'}",
        ]
        if prefs:
            lines.append("preferences:")
            lines += [f"  {k}: {v}" for k, v in prefs.items()]
        for part in split_message("\n".join(lines)):
            await update.message.reply_text(part)
    finally:
        db.close()


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /research <topic>")
        return
    topic = " ".join(context.args)
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        await _ensure_model(db, user)
        system = user.system_prompt or "You are a deep research assistant."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Do deep research on: {topic}. Provide a structured report with cited points and a conclusion."},
        ]
        await update.message.reply_text("🔍 در حال پژوهش...")
        reply = await asyncio.to_thread(chat_completion, user, messages)
        memory.add_message(db, user, "user", f"/research {topic}")
        memory.add_message(db, user, "assistant", reply, model_used=user.active_model)
        for part in split_message(reply):
            await update.message.reply_text(part)
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا: {e}")
    finally:
        db.close()


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in _admin_ids():
        await update.message.reply_text("⛔ فقط ادمین.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <msg>")
        return
    msg = " ".join(context.args)
    db = _db()
    try:
        sent = 0
        for u in memory.all_users(db):
            try:
                await context.bot.send_message(u.telegram_id, f"📢 {msg}")
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ ارسال شد به {sent} نفر.")
    finally:
        db.close()


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    db = _db()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        await _ensure_model(db, user)
        system = user.system_prompt or DEFAULT_SYSTEM_PROMPT
        history = memory.get_history(db, user)
        messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": text}]
        await update.message.chat.send_action("typing")
        try:
            reply = await asyncio.to_thread(_agentic_reply, user, messages)
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطا: {e}")
            return
        memory.add_message(db, user, "user", text)
        memory.add_message(db, user, "assistant", reply, model_used=user.active_model)
        for part in split_message(reply):
            await update.message.reply_text(part)
        if user.tts_enabled:
            try:
                ogg = await asyncio.to_thread(text_to_speech, user, reply)
                with open(ogg, "rb") as f:
                    await update.message.reply_voice(f)
                os.remove(ogg)
            except Exception as e:
                print(f"[tts] failed: {e}")
    finally:
        db.close()
