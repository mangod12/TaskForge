"""
Async SQLAlchemy engine and session factory.
Compatible with PostgreSQL / AlloyDB (standard wire protocol).
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

is_cloud_run = bool(os.getenv("K_SERVICE"))
pool_size = 5 if is_cloud_run else 20
max_overflow = 5 if is_cloud_run else 10

engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level == "DEBUG" and not is_cloud_run,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,
    pool_recycle=1800,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:  # type: ignore[misc]
    """Dependency-injectable session generator."""
    async with async_session_factory() as session:
        yield session
