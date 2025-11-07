"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from ..core.config import config


# Create database engine
engine = create_engine(
    config.database_url,
    pool_size=config.database_pool_size,
    max_overflow=config.database_max_overflow,
    echo=config.api_debug
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Get database session (alias for compatibility)."""
    return SessionLocal()


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


def reset_database() -> None:
    """Reset database by dropping and recreating all tables."""
    drop_tables()
    create_tables()