"""
Database connection management for Data Ingestion Agent.

Provides async connection pooling using SQLAlchemy with asyncpg driver.
Supports Railway PostgreSQL deployment with automatic URL detection.
"""

import logging
import asyncio
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy import text

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Async PostgreSQL connection manager.

    Handles connection pooling, health checks, and session management.
    """

    def __init__(
        self,
        database_url: str,
        pool_min_size: int = 5,
        pool_max_size: int = 20,
        echo: bool = False
    ):
        """
        Initialize database connection manager.

        Args:
            database_url: PostgreSQL connection URL
            pool_min_size: Minimum connections in pool
            pool_max_size: Maximum connections in pool
            echo: Enable SQL logging
        """
        # Convert postgres:// to postgresql+asyncpg://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif not database_url.startswith("postgresql+asyncpg://"):
            database_url = f"postgresql+asyncpg://{database_url}"

        self._database_url = database_url
        self._pool_min_size = pool_min_size
        self._pool_max_size = pool_max_size
        self._echo = echo

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database engine and session factory."""
        if self._initialized:
            return

        try:
            logger.info("Initializing database connection pool...")

            self._engine = create_async_engine(
                self._database_url,
                echo=self._echo,
                pool_size=self._pool_min_size,
                max_overflow=self._pool_max_size - self._pool_min_size,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections after 1 hour
            )

            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )

            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            self._initialized = True
            logger.info("Database connection pool initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    async def close(self) -> None:
        """Close the database engine and all connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session from the pool.

        Yields:
            AsyncSession: Database session for queries

        Example:
            async with db.session() as session:
                result = await session.execute(query)
        """
        if not self._initialized:
            await self.initialize()

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def health_check(self) -> dict:
        """
        Check database connection health.

        Returns:
            dict with status, latency, and pool info
        """
        import time
        start = time.time()

        try:
            if not self._initialized:
                await self.initialize()

            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as check, NOW() as server_time"))
                row = result.fetchone()

            latency_ms = (time.time() - start) * 1000

            # Get pool stats
            pool_status = {
                "pool_size": self._engine.pool.size() if hasattr(self._engine.pool, 'size') else "N/A",
                "checked_in": self._engine.pool.checkedin() if hasattr(self._engine.pool, 'checkedin') else "N/A",
                "checked_out": self._engine.pool.checkedout() if hasattr(self._engine.pool, 'checkedout') else "N/A",
            }

            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "server_time": str(row.server_time) if row else None,
                "pool": pool_status
            }

        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": round(latency_ms, 2)
            }

    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Get the SQLAlchemy async engine."""
        return self._engine

    @property
    def is_initialized(self) -> bool:
        """Check if connection pool is initialized."""
        return self._initialized


# Global connection instance (lazy initialization)
_db_connection: Optional[DatabaseConnection] = None


async def get_db_connection() -> DatabaseConnection:
    """
    Get the global database connection instance.

    Lazy initializes the connection on first call.

    Returns:
        DatabaseConnection instance
    """
    global _db_connection

    if _db_connection is None:
        from data_ingestion.settings import get_data_ingestion_settings

        settings = get_data_ingestion_settings()
        if not settings.DATABASE_URL:
            raise RuntimeError(
                "DATA_INGESTION_DATABASE_URL environment variable not set. "
                "Please configure PostgreSQL connection for data ingestion."
            )

        _db_connection = DatabaseConnection(
            database_url=settings.DATABASE_URL,
            pool_min_size=settings.DB_POOL_MIN_SIZE,
            pool_max_size=settings.DB_POOL_MAX_SIZE,
            echo=settings.DB_ECHO
        )

    if not _db_connection.is_initialized:
        await _db_connection.initialize()

    return _db_connection


async def close_db_connection() -> None:
    """Close the global database connection."""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None
