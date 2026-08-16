# OmniAgent — Telegram AI Agent

ربات تلگرامی **خودمیزبان (self-hosted)** و **چندوجهی (multimodal)** که به هر اندپوینت
سازگار با OpenAI وصل می‌شود. مدل‌ها را خودش از اندپوینت می‌خواند، پس نیازی نیست نام مدل
را دستی بنویسید. چت آزاد، تحلیل تصویر (vision)، خروجی صدا (TTS) و ورودی صدا (STT) دارد و
حافظه بلندمدت را در SQL نگه می‌دارد (SQLite برای محلی/Termux، Postgres برای Railway).

> کلید API هر کاربر با **Fernet** رمزنگاری می‌شود و در دیتابیس ذخیره می‌گردد.

---

## ویژگی‌ها

- **اندپوینت دلخواه**: هر سرویسی که فرمت OpenAI-compatible داشته باشد (Ollama، vLLM،
  LM Studio، OpenRouter، هوستینگ‌های شخصی و …).
- **کشف خودکار مدل‌ها**: دستور `/models` لیست مدل‌ها را از اندپوینت می‌آورد.
- **چت + تصویر + صدا**: پاسخ متنی، تحلیل عکس، تبدیل متن به گفتار و گفتار به متن.
- **حافظه بلندمدت**: تاریخچه مکالمه در SQL با پنجره حافظه قابل‌تنظیم.
- **پروفایل هر کاربر**: سیستم‌پرامپت، مدل فعال، صدا و تنظیمات دلخواه به تفکیک تلگرام‌آیدی.
- **فال‌بک SQLite**: بدون هیچ تنظیمی روی Termux/لوکال اجرا می‌شود.

---

## پیش‌نیازها

- Python 3.10+
- کتابخانه‌های `requirements.txt`
- (برای صدا) `ffmpeg` روی سیستم نصب باشد
- یک توکن ربات از [@BotFather](https://t.me/BotFather)

---

## راه‌اندازی سریع (محلی / Termux)

```bash
# ۱) کلون
git clone https://github.com/azarnezam0-crypto/telegram-ai-agent.git
cd telegram-ai-agent

# ۲) نصب وابستگی‌ها
pip install -r requirements.txt

# ۳) ساخت فایل محیطی
cp .env.example .env
nano .env
#    فقط TELEGRAM_BOT_TOKEN را پر کن. بقیه اختیاری‌اند.
#    اگر DATABASE_URL را خالی بگذاری، ربات از SQLite (agent.db) استفاده می‌کند.

# ۴) اجرا
python bot.py
```

نمونه `.env` کمینه:

```ini
TELEGRAM_BOT_TOKEN=123456:ABC-your-token
# DATABASE_URL خالی بماند -> SQLite
```

---

## استقرار روی Railway (Postgres)

1. ریپو را به Railway متصل کنید (New → Deploy from GitHub repo).
2. افزونه **PostgreSQL** اضافه کنید؛ Railway متغیر `DATABASE_URL` را می‌سازد.
3. متغیرهای محیطی را ست کنید:

```ini
TELEGRAM_BOT_TOKEN=...
DATABASE_URL=postgresql://...   # توسط Railway ساخته می‌شود
ENCRYPTION_KEY=...              # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DEFAULT_BASE_URL=https://api.openai.com/v1
DEFAULT_API_KEY=
DEFAULT_MODEL=gpt-4o
MEMORY_WINDOW=20
```

4. `Procfile` از قبل روی `worker: python bot.py` تنظیم شده — ربات به صورت polling اجرا
   می‌شود (نیازی به پورت HTTP ندارد). پروسس را روی نوع **worker** قرار دهید.

تولید `ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## دستورات ربات

| دستور | کار |
|-------|-----|
| `/start` | خوش‌آمدگویی و ساخت پروفایل |
| `/help` | راهنمای فارسی |
| `/setapi <base_url> <api_key>` | تنظیم اندپوینت و کلید (رمزنگاری‌شده) |
| `/models` | دریافت لیست مدل‌ها از اندپوینت |
| `/setmodel <name>` | انتخاب مدل فعال |
| `/setsystem <text>` | تنظیم سیستم‌پرامپت |
| `/setmemory <n>` | اندازه پنجره حافظه (تعداد پیام) |
| `/tts on|off` | خروجی صدا روشن/خاموش |
| `/profile` | نمایش تنظیمات فعلی |
| `/history` | ۱۰ پیام آخر |
| `/forget` | پاک کردن حافظه |
| `/newchat` | شروع چت جدید (پاکسازی تاریخچه) |
| `/research <q>` | پاسخ چندبخشی/مفصل |
| `/setpref <key> <value>` | ذخیره تنظیم دلخواه |

### اولین بار چطور راه بیندازیم؟

```
/setapi https://your-endpoint/v1 sk-xxxxxx
/models
/setmodel gpt-4o-mini
/tts on        (اختیاری)
سلام!
```

---

## ساختار پروژه

```
telegram-ai-agent/
├── bot.py                  # نقطه ورود + ثبت دستورات + error handler
├── db/
│   ├── models.py           # جداول SQLAlchemy
│   └── session.py          # engine + init_db + get_db
├── services/
│   ├── llm_client.py       # کلاینت OpenAI + fetch_models + chat/vision/transcribe
│   ├── memory_service.py   # مدیریت کاربر/تاریخچه/تنظیمات
│   └── tts_service.py      # تبدیل متن به گفتار (mp3 -> opus)
├── handlers/
│   ├── chat_handlers.py    # دستورات چت + handle_text
│   ├── media_handlers.py   # عکس و voice
│   └── memory_handlers.py  # history/forget/newchat/setpref
├── requirements.txt
├── Dockerfile
├── railway.toml
├── Procfile                # worker: python bot.py
└── .env.example
```

---

## نکات امنیتی

- کلید API در `.env` است — **هرگز `.env` را کامیت نکنید** (در `.gitignore` آمده است).
- `ENCRYPTION_KEY` را فقط یک بار بسازید و ثابت نگه دارید؛ با تغییر آن کلیدهای رمزنگاری‌شده
  قبلی دیگر باز نمی‌شوند.
- فقط **یک نمونه** از ربات را با یک توکن اجرا کنید؛ اجرای همزمان دو نمونه (مثلاً Railway + Termux)
  باعث خطای ۴۰۹ Conflict در polling می‌شود.

---

## عیب‌یابی

- **`No error handlers are registered`**: ربات خطای داخلی داشته؛ با `make run-debug` یا
  `python bot.py` لاگ کامل را ببینید.
- **۴۰۹ Conflict**: دو نمونه با یک توکن در حال اجرا هستند. یکی را خاموش کنید.
- **مدل پیدا نمی‌شود / ۴۰۴**: `base_url` را چک کنید (`/setapi`) و با `/models` لیست را بخوانید.
- **خطای صدا**: مطمئن شوید `ffmpeg` نصب است (`ffmpeg -version`).
