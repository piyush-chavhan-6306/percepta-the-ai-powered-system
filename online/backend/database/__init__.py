"""
PERCEPTA Unified Database Package (PostgreSQL Neon + SQLite Engine).
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

try:
    from backend.database.core import (
        Base,
        init_db,
        close_db,
        get_session_factory,
        get_db_session,
    )
except ImportError:
    from database.core import (
        Base,
        init_db,
        close_db,
        get_session_factory,
        get_db_session,
    )

try:
    from backend.database.neon_adapter import (
        init_cloud_db,
        get_neon_database_url,
    )
except ImportError:
    from database.neon_adapter import (
        init_cloud_db,
        get_neon_database_url,
    )

__all__ = [
    "Base",
    "init_db",
    "close_db",
    "get_session_factory",
    "get_db_session",
    "init_cloud_db",
    "get_neon_database_url",
]
