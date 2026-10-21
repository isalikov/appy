from redis.asyncio import Redis

from appy_api.settings import Settings


def create_client(settings: Settings) -> Redis:
    return Redis.from_url(str(settings.redis_dsn), decode_responses=True)


async def ping(client: Redis) -> None:
    await client.ping()
