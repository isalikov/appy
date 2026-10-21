from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import partial

from pymongo import AsyncMongoClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from appy_api.db import mongo, postgres, redis
from appy_api.settings import Settings

type Probe = Callable[[], Awaitable[None]]


@dataclass(slots=True)
class Resources:
    """Process-wide clients, created once in the app lifespan."""

    engine: AsyncEngine
    sessions: async_sessionmaker[AsyncSession]
    mongo: AsyncMongoClient[mongo.MongoDocument]
    redis: Redis
    probes: dict[str, Probe] = field(default_factory=dict)

    @classmethod
    def create(cls, settings: Settings) -> Resources:
        engine = postgres.create_engine(settings)
        mongo_client = mongo.create_client(settings)
        redis_client = redis.create_client(settings)
        return cls(
            engine=engine,
            sessions=postgres.create_session_factory(engine),
            mongo=mongo_client,
            redis=redis_client,
            probes={
                "postgres": partial(postgres.ping, engine),
                "mongo": partial(mongo.ping, mongo_client),
                "redis": partial(redis.ping, redis_client),
            },
        )

    async def close(self) -> None:
        await self.redis.aclose()
        await self.mongo.close()
        await self.engine.dispose()
