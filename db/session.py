import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

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
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
