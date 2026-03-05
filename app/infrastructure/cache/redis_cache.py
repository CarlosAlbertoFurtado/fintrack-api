from typing import Optional

import redis.asyncio as redis

from app.config import settings
from app.domain.interfaces.repositories import ICacheService
from app.shared.logger import logger


class RedisCacheService(ICacheService):
    def __init__(self) -> None:
        self.client = redis.from_url(
            settings.redis_url, decode_responses=True, retry_on_timeout=True,
        )

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.client.get(key)
        except redis.RedisError as e:
            logger.warning("redis_get_error", error=str(e))
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        try:
            await self.client.set(key, value, ex=ttl_seconds)
        except redis.RedisError as e:
            logger.warning("redis_set_error", error=str(e))

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except redis.RedisError as e:
            logger.warning("redis_delete_error", error=str(e))

    async def delete_pattern(self, pattern: str) -> None:
        try:
            keys = [key async for key in self.client.scan_iter(match=pattern)]
            if keys:
                await self.client.delete(*keys)
        except redis.RedisError as e:
            logger.warning("redis_delete_pattern_error", error=str(e))

    async def disconnect(self) -> None:
        await self.client.close()
