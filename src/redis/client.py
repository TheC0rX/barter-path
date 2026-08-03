from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage

from src.config import config

redis_client = Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)

storage = RedisStorage(redis=redis_client)
