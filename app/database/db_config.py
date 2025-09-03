import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings

settings = get_settings()

# Prefer env-provided URL, fallback for local dev if absent
database_url: Optional[str] = os.getenv("DATABASE_URL") or (str(settings.DATABASE_URL) if settings.DATABASE_URL else None)
if not database_url:
    # Safe local default (SQLite). Users can override via .env
    database_url = "sqlite:///./app.db"

# Create database engine (sync). For SQLite enable check_same_thread.
engine_kwargs = {}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_engine(database_url, **engine_kwargs)


# Session and Base for SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the database session
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_database()