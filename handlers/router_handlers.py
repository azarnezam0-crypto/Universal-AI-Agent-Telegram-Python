"""9Router capability handlers: image generation, web search, web fetch."""
import asyncio
import base64
import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from db.session import SessionLocal
from services.llm_client import generate_image
from services.router_client import web_search, web_fetch
from services.memory_service import MemoryService
from services.message_utils import split_message

memory = MemoryService()


async def cmd_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /image <prompt> [--size 1024x1024]")
        return
    args = list(context.args)
    size = None
    if "--size" in args:
        i = args.index("--size")
        size = args[i + 1] if i + 1 < len(args) else None
        args = args[:i] + args[i + 2:]
    prompt = " ".join(args)

    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        await update.message.reply_text("🎨 در حال ساخت عکس...")
        try:
            result = await asyncio.to_thread(generate_image, user, prompt, size=size)
        except Exception as e:
            await update.message.reply_text(f"⚠️ ساخت عکس شکست خورد: {e}")
            return
        url = result.get("url")
        b64 = result.get("b64_json")
        if url:
            await update.message.reply_photo(url, caption=prompt[:200])
        elif b64:
            path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
            with open(path, "rb") as f:
                await update.message.reply_photo(f, caption=prompt[:200])
            os.remove(path)
        else:
            await update.message.reply_text("⚠️ پاسخی برای عکس دریافت نشد.")
    finally:
        db.close()


async def cmd_web(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /web <query>")
        return
    query = " ".join(context.args)

    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        await update.message.reply_text("🔍 در حال جستجو...")
        try:
            data = await asyncio.to_thread(web_search, user, query, 5)
        except Exception as e:
            await update.message.reply_text(f"⚠️ جستجو شکست خورد: {e}")
            return
        results = data.get("results") or []
        if not results:
            await update.message.reply_text("نتیجه‌ای پیدا نشد.")
            return
        lines = []
        for i, r in enumerate(results[:8], 1):
            title = r.get("title") or "(بدون عنوان)"
            url = r.get("url") or ""
            snippet = (r.get("snippet") or "").strip()
            lines.append(f"{i}. {title}\n{url}\n{snippet}")
        text = f"🔎 نتایج برای «{query}»:\n\n" + "\n\n".join(lines)
        for part in split_message(text):
            await update.message.reply_text(part)
    finally:
        db.close()


async def cmd_fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /fetch <url>")
        return
    url = context.args[0]

    db = SessionLocal()
    try:
        user = memory.get_or_create_user(db, update.effective_user.id)
        await update.message.reply_text("📄 در حال بارگیری صفحه...")
        try:
            data = await asyncio.to_thread(web_fetch, user, url, "markdown", 8000)
        except Exception as e:
            await update.message.reply_text(f"⚠️ بارگیری شکست خورد: {e}")
            return
        content = data.get("content") or {}
        text = content.get("text") if isinstance(content, dict) else None
        if not text:
            text = data.get("content") or ""
        title = data.get("title") or url
        if not text:
            await update.message.reply_text("⚠️ محتوایی استخراج نشد.")
            return
        full = f"📄 {title}\n\n{text}"
        for part in split_message(full):
            await update.message.reply_text(part)
    finally:
        db.close()
