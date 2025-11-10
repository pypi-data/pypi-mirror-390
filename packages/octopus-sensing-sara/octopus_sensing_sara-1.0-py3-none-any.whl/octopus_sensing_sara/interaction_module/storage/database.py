"""Database connection and session management."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from octopus_sensing_sara.core.config import get_settings
from octopus_sensing_sara.models.database import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    _engine: AsyncEngine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Get or create the database engine.

        Returns:
            AsyncEngine: SQLAlchemy async engine instance

        Raises:
            RuntimeError: If engine creation fails
        """
        if cls._engine is None:
            try:
                settings = get_settings()
                cls._engine = create_async_engine(
                    settings.database_url,
                    echo=settings.debug,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10,
                )
                logger.info(f"Database engine created: {settings.database_url}")
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise RuntimeError(f"Database engine creation failed: {e}") from e
        return cls._engine

    @classmethod
    def get_sessionmaker(cls) -> async_sessionmaker[AsyncSession]:
        """Get or create the session maker.

        Returns:
            async_sessionmaker: SQLAlchemy async session maker
        """
        if cls._sessionmaker is None:
            engine = cls.get_engine()
            cls._sessionmaker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            logger.info("Database session maker created")
        return cls._sessionmaker

    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session as an async context manager.

        Yields:
            AsyncSession: Database session

        Example:
            async with DatabaseManager.get_session() as session:
                result = await session.execute(select(User))
        """
        sessionmaker = cls.get_sessionmaker()
        session = sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

    @classmethod
    async def init_db(cls) -> None:
        """Initialize database by creating all tables.

        This should be called during application startup.
        """
        try:
            engine = cls.get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @classmethod
    async def close(cls) -> None:
        """Close database connections.

        This should be called during application shutdown.
        """
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._engine = None
            cls._sessionmaker = None
            logger.info("Database connections closed")
