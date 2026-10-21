"""Relational models. Import every model module here so Alembic autogenerate
sees the full metadata."""

from appy_api.db.postgres import Base

__all__ = ["Base"]
