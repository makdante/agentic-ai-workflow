#src/core/database/connection.py
"""
Database connection utilities and session management.
Provides helper functions for database operations and connection handling.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, TypeVar, Generic

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text


from config.database import get_db_session, SessionLocal
from config.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class DatabaseConnection:
    """Database connection wrapper with error handling and logging."""
    
    def __init__(self):
        self.session_factory = SessionLocal
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_factory()
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with get_db_session() as session:
                session.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_with_retry(self, operation, max_retries: int = 3) -> Optional[any]:
        """
        Execute database operation with retry logic.
        
        Args:
            operation: Function to execute
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result of the operation or None if failed
        """
        for attempt in range(max_retries):
            try:
                with get_db_session() as session:
                    result = operation(session)
                    logger.debug(f"Database operation successful on attempt {attempt + 1}")
                    return result
            except SQLAlchemyError as e:
                logger.warning(f"Database operation failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Database operation failed after {max_retries} attempts")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in database operation: {e}")
                raise
        
        return None


class TransactionManager:
    """Context manager for database transactions with automatic rollback."""
    
    def __init__(self, session: Session):
        self.session = session
        self.transaction = None
    
    def __enter__(self):
        self.transaction = self.session.begin()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Transaction failed, rolling back: {exc_val}")
            self.transaction.rollback()
        else:
            self.transaction.commit()
            logger.debug("Transaction committed successfully")


@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[Session, None]:
    """
    Async context manager for database sessions.
    Note: This is a placeholder for future async implementation.
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


def with_db_session(func):
    """
    Decorator to automatically provide database session to functions.
    
    Usage:
        @with_db_session
        def my_function(session: Session, other_args):
            # Use session here
            pass
    """
    def wrapper(*args, **kwargs):
        with get_db_session() as session:
            return func(session, *args, **kwargs)
    return wrapper


def safe_db_operation(operation_name: str = "database operation"):
    """
    Decorator for safe database operations with error handling.
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Starting {operation_name}")
                result = func(*args, **kwargs)
                logger.debug(f"Completed {operation_name} successfully")
                return result
            except SQLAlchemyError as e:
                logger.error(f"{operation_name} failed with SQLAlchemy error: {e}")
                raise
            except Exception as e:
                logger.error(f"{operation_name} failed with unexpected error: {e}")
                raise
        return wrapper
    return decorator


class ConnectionPool:
    """Database connection pool manager."""
    
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self._is_healthy = True
    
    def health_check(self) -> bool:
        """Perform health check on database connection."""
        try:
            self._is_healthy = self.db_connection.test_connection()
            return self._is_healthy
        except Exception as e:
            logger.error(f"Connection pool health check failed: {e}")
            self._is_healthy = False
            return False
    
    def get_connection_stats(self) -> dict:
        """Get connection pool statistics."""
        return {
            "is_healthy": self._is_healthy,
            "pool_size": self.db_connection.session_factory.kw.get("pool_size", "unknown"),
            "checked_out": "unknown",  # SQLite doesn't provide this info
            "overflow": "unknown",
            "checked_in": "unknown"
        }
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        try:
            self.db_connection.session_factory.bind.dispose()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global connection pool instance
connection_pool = ConnectionPool()