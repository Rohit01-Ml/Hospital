"""SQLAlchemy database engine and session factory.

Local development: falls back to SQLite if DATABASE_URL is not set.
Production: set DATABASE_URL to PostgreSQL connection string.
  postgresql://user:pass@host:5432/dbname
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

DATABASE_URL: str = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./hospital.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
