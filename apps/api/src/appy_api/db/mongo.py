from typing import Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from appy_api.settings import Settings

type MongoDocument = dict[str, Any]


def create_client(settings: Settings) -> AsyncMongoClient[MongoDocument]:
    return AsyncMongoClient(str(settings.mongo_dsn), tz_aware=True, uuidRepresentation="standard")


def get_database(
    client: AsyncMongoClient[MongoDocument], settings: Settings
) -> AsyncDatabase[MongoDocument]:
    return client[settings.mongo_db]


async def ping(client: AsyncMongoClient[MongoDocument]) -> None:
    await client.admin.command("ping")
