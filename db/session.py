import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.models import Base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# fallback to SQLite for local/Termux use
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./agent.db"
    print("⚠️  No DATABASE_URL found — using SQLite (local mode)")

# Railway Postgres fix: replace postgres:// with postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db():
    # 1) create tables that don't exist yet
    Base.metadata.create_all(bind=engine)
    # 2) add any missing columns to tables that already exist (e.g. an older
    #    Postgres 'users' table lacking base_url / api_key_encrypted / tts_enabled / ...)
    #    Hardcoded + idempotent (ADD COLUMN IF NOT EXISTS) so it can't fail on a
    #    column that's already there, and doesn't depend on schema introspection.
    _sync_missing_columns()


def _sync_missing_columns():
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);
            ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(200);
            ALTER TABLE users ADD COLUMN IF NOT EXISTS base_url VARCHAR(500);
            ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key_encrypted TEXT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS active_model VARCHAR(200);
            ALTER TABLE users ADD COLUMN IF NOT EXISTS system_prompt TEXT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS tts_enabled BOOLEAN;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS tts_voice VARCHAR(50);
            ALTER TABLE users ADD COLUMN IF NOT EXISTS memory_window INTEGER;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS current_session_id INTEGER;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;
        """))
    logger.info("init_db: synced users columns (added any that were missing)")
    # The 'sessions' table may predate columns added to the model (e.g. it was
    # created by an older create_all without telegram_id). create_all only makes
    # missing TABLES, not missing columns, so patch them here idempotently.
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE sessions ADD COLUMN IF NOT EXISTS telegram_id BIGINT;
            ALTER TABLE sessions ADD COLUMN IF NOT EXISTS started_at TIMESTAMP;
            ALTER TABLE sessions ADD COLUMN IF NOT EXISTS ended_at TIMESTAMP;
            ALTER TABLE sessions ADD COLUMN IF NOT EXISTS message_count INTEGER;
        """))
    logger.info("init_db: synced sessions columns (added any that were missing)")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
