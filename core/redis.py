from typing import Optional

import redis.asyncio as redis

from .config import settings


class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self, url: str = settings.redis_url):
        self.client = await redis.from_url(
            url, decode_responses=True, max_connections=10, socket_connect_timeout=5
        )

    async def disconnect(self):
        if self.client:
            await self.client.aclose()


redis_manager = RedisManager()
