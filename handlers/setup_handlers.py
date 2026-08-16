from telegram.ext import CommandHandler, MessageHandler, filters

from .chat_handlers import (
    cmd_start,
    cmd_help,
    cmd_setapi,
    cmd_models,
    cmd_setmodel,
    cmd_setsystem,
    cmd_setmemory,
    cmd_tts,
    cmd_profile,
    cmd_research,
    cmd_broadcast,
    handle_text,
)
from .media_handlers import handle_photo, handle_voice
from .memory_handlers import cmd_history, cmd_forget, cmd_setpref, cmd_sessions, cmd_newchat, cmd_resume, cmd_clearprefs
from .router_handlers import cmd_image, cmd_web, cmd_fetch


def register_handlers(app):
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("setapi", cmd_setapi))
    app.add_handler(CommandHandler("models", cmd_models))
    app.add_handler(CommandHandler("setmodel", cmd_setmodel))
    app.add_handler(CommandHandler("setsystem", cmd_setsystem))
    app.add_handler(CommandHandler("setmemory", cmd_setmemory))
    app.add_handler(CommandHandler("tts", cmd_tts))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("sessions", cmd_sessions))
    app.add_handler(CommandHandler("newchat", cmd_newchat))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("forget", cmd_forget))
    app.add_handler(CommandHandler("setpref", cmd_setpref))
    app.add_handler(CommandHandler("clearprefs", cmd_clearprefs))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("image", cmd_image))
    app.add_handler(CommandHandler("web", cmd_web))
    app.add_handler(CommandHandler("fetch", cmd_fetch))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
