import os
import logging
from sqlalchemy import create_engine
from typing import Generator, Optional
from sqlalchemy.orm import sessionmaker
from app.core.settings import get_settings
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
database_url: Optional[str] = os.getenv("DATABASE_URL") or (str(settings.DATABASE_URL) if settings.DATABASE_URL else None)
if not database_url:
    database_url = os.getenv("SQLALCHEMY_DATABASE_URL")
engine_kwargs = {}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_engine(database_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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