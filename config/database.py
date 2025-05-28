#config/database.py
"""
Database configuration and connection management.
Handles SQLite connections, session management, and database initialization.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import text


from config.settings import get_settings

settings = get_settings()

# SQLite-specific configuration for better performance
def _sqlite_pragma_on_connect(dbapi_con, connection_record):
    """Configure SQLite pragmas for better performance and reliability."""
    dbapi_con.execute("PRAGMA foreign_keys=ON")
    dbapi_con.execute("PRAGMA journal_mode=WAL")
    dbapi_con.execute("PRAGMA synchronous=NORMAL")
    dbapi_con.execute("PRAGMA temp_store=memory")
    dbapi_con.execute("PRAGMA mmap_size=268435456")  # 256MB

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "check_same_thread": False,  # Allow SQLite to be used across threads
        "timeout": 30
    }
)

# Add SQLite pragma configuration
event.listen(engine, "connect", _sqlite_pragma_on_connect)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()


def get_database_engine() -> Engine:
    """Get the database engine instance."""
    return engine


def get_session_factory() -> sessionmaker:
    """Get the session factory."""
    return SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session with automatic cleanup.
    
    Usage:
        with get_db_session() as session:
            # Use session here
            session.query(Model).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> None:
    """
    Initialize the database by creating all tables.
    This should be called during application startup.
    """
    try:
        # Import all models to ensure they are registered
        from src.core.database.models import (
            Repository,
            CodeAnalysis,
            Suggestion,
            WorkflowState
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


class DatabaseManager:
    """Database manager for handling connections and transactions."""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_factory()
    
    def close_all_sessions(self) -> None:
        """Close all database sessions."""
        self.engine.dispose()
    
    def execute_raw_sql(self, sql: str, params: dict = None) -> any:
        """Execute raw SQL query."""
        with get_db_session() as session:
            result = session.execute(sql, params or {})
            return result.fetchall()


# Global database manager instance
db_manager = DatabaseManager()