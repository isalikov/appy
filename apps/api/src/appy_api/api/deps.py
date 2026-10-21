from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from appy_api.db import mongo
from appy_api.db.postgres import session_scope
from appy_api.resources import Probe, Resources
from appy_api.settings import Settings


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_resources(request: Request) -> Resources:
    resources: Resources = request.app.state.resources
    return resources


ResourcesDep = Annotated[Resources, Depends(get_resources)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_session(resources: ResourcesDep) -> AsyncIterator[AsyncSession]:
    async for session in session_scope(resources.sessions):
        yield session


def get_mongo(resources: ResourcesDep, settings: SettingsDep) -> AsyncDatabase[mongo.MongoDocument]:
    return mongo.get_database(resources.mongo, settings)


def get_redis(resources: ResourcesDep) -> Redis:
    return resources.redis


def get_probes(resources: ResourcesDep) -> dict[str, Probe]:
    return resources.probes


SessionDep = Annotated[AsyncSession, Depends(get_session)]
MongoDep = Annotated[AsyncDatabase[mongo.MongoDocument], Depends(get_mongo)]
RedisDep = Annotated[Redis, Depends(get_redis)]
ProbesDep = Annotated[dict[str, Probe], Depends(get_probes)]
