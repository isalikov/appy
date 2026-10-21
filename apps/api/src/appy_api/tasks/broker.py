"""Background task queue on Redis streams.

Run a worker with: `uv run taskiq worker appy_api.tasks.broker:broker appy_api.tasks.jobs`
"""

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from appy_api.settings import get_settings

_tasks_dsn = str(get_settings().tasks_redis_dsn)

broker = RedisStreamBroker(url=_tasks_dsn).with_result_backend(
    RedisAsyncResultBackend(redis_url=_tasks_dsn, result_ex_time=3600)
)
