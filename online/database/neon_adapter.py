"""
PERCEPTA ONLINE NEON POSTGRESQL ADAPTER
Manages cloud database engine connection to Neon PostgreSQL (or local fallback)
with asynchronous connection pooling and tenant isolation schemas.
"""
import os
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_online_engine: AsyncEngine | None = None
_online_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_neon_database_url() -> str:
    """Retrieve Neon PostgreSQL async URL, converting postgres:// to postgresql+asyncpg:// if needed."""
    url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./percepta_cloud.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def init_cloud_db(db_url: str | None = None) -> AsyncEngine:
    global _online_engine, _online_session_factory
    url = db_url or get_neon_database_url()
    
    is_sqlite = "sqlite" in url
    
    _online_engine = create_async_engine(
        url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
    
    async with _online_engine.begin() as conn:
        try:
            import database.models
        except ImportError:
            import online.database.models
        if is_sqlite:
            await conn.execute(text("PRAGMA journal_mode=WAL;"))
            await conn.execute(text("PRAGMA busy_timeout=5000;"))
        await conn.run_sync(Base.metadata.create_all)
        
    _online_session_factory = async_sessionmaker(
        bind=_online_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return _online_engine


async def get_cloud_db_session() -> AsyncGenerator[AsyncSession, None]:
    global _online_session_factory
    if _online_session_factory is None:
        await init_cloud_db()
    assert _online_session_factory is not None
    async with _online_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
