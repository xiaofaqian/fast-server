import aioredis
from app.core.config import settings

class Redis:
    client = None

async def connect_to_redis():
    Redis.client = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis_connection():
    if Redis.client:
        await Redis.client.close()

def get_redis():
    return Redis.client
