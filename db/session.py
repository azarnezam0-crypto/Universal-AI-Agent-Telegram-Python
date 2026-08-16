import logging
import os
from sqlalchemy import create_engine, inspect, text
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
    _sync_missing_columns()


def _sync_missing_columns():
    insp = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.tables.values():
            if not insp.has_table(table.name):
                continue
            existing = {c["name"] for c in insp.get_columns(table.name)}
            for col in table.columns:
                if col.name in existing:
                    continue
                # Add as nullable so it never fails on rows that already exist.
                # Python-side defaults in the models fill the value on insert.
                conn.execute(
                    text(f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {col.type}')
                )
                logger.info("init_db: added missing column %s.%s", table.name, col.name)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
