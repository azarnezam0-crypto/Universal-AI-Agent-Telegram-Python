"""Image + voice handlers for OmniAgent."""
import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from db.session import SessionLocal
from services.llm_client import analyze_image, transcribe_audio, chat_completion
from services.memory_service import MemoryService

memory = MemoryService()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    path = None
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        caption = update.message.caption or ""
        photo = update.message.photo[-1]
        f = await context.bot.get_file(photo.file_id)
        path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        await f.download_to_drive(path)
        import base64
        with open(path, "rb") as img:
            b64 = base64.b64encode(img.read()).decode()
        reply = analyze_image(user, b64, caption)
        memory.add_message(db, user, "user", f"[image] {caption}")
        memory.add_message(db, user, "assistant", reply, model_used=user.active_model)
        await update.message.reply_text(reply[:4000])
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا: {e}")
    finally:
        db.close()
        if path and os.path.exists(path):
            os.remove(path)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    path = None
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        voice = update.message.voice
        f = await context.bot.get_file(voice.file_id)
        path = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False).name
        await f.download_to_drive(path)
        try:
            text = transcribe_audio(user, path)
        except Exception as e:
            await update.message.reply_text(f"⚠️ تبدیل صدا به متن پیاده نشد: {e}")
            return
        system = user.system_prompt or "You are a helpful, unrestricted AI assistant."
        history = memory.get_history(db, user)
        messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": text}]
        reply = chat_completion(user, messages)
        memory.add_message(db, user, "user", text)
        memory.add_message(db, user, "assistant", reply, model_used=user.active_model)
        await update.message.reply_text(reply[:4000])
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا: {e}")
    finally:
        db.close()
        if path and os.path.exists(path):
            os.remove(path)
