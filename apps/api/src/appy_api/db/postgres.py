from collections.abc import AsyncIterator

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from appy_api.settings import Settings

# Deterministic constraint names keep Alembic autogenerate diffs stable.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for every relational model. Vector columns use
    `pgvector.sqlalchemy.Vector(dim)`."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        str(settings.postgres_dsn),
        pool_size=settings.postgres_pool_size,
        max_overflow=settings.postgres_max_overflow,
        pool_pre_ping=True,
        echo=settings.postgres_echo,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def session_scope(factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """One session per request; commits on success, rolls back on error."""
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise


async def ping(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
