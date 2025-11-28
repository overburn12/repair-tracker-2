"""
Infrastructure Layer: Database Connection Management

This module handles database engine, session factory, and session lifecycle.
It provides the connection infrastructure for the data access layer.
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db_models import Base


# Get database URL from environment variable
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/repair_tracker'
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session() -> Generator[Session, None, None]:
    """
    Provide a database session for dependency injection.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        Used with FastAPI's Depends() for automatic session management
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """
    Initialize database tables.

    Note: This should typically not be called in production since
    the database schema is frozen and contains production data.
    """
    Base.metadata.create_all(bind=engine)
