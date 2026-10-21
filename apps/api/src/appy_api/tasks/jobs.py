from appy_api.tasks.broker import broker


@broker.task
async def echo(message: str) -> str:
    """Example task; replace with real jobs."""
    return message
