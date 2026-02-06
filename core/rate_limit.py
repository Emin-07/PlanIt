import time

from fastapi import Depends, HTTPException, Request, status

from auth.services.validation import get_current_auth_user

from .config import settings
from .redis import redis_manager


async def check_rate_limit(id: str, prefix: str, limit: int, window: int):
    key = f"rate_limit:{prefix}:{id}"
    current_time = time.time()

    await redis_manager.client.zremrangebyscore(key, 0, current_time - window)

    request_count = await redis_manager.client.zcard(key)

    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. {limit} requests per {window} seconds",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(window),
            },
        )

    await redis_manager.client.zadd(key, {str(current_time): current_time})
    await redis_manager.client.expire(key, window + 10)

    return {
        "limit": limit,
        "remaining": limit - request_count - 1,
        "reset": int(current_time + window),
    }


async def get_global_rate_limit(request: Request):
    return await check_rate_limit(
        id=request.client.host,
        prefix="global",
        limit=settings.redis_limit_global,
        window=settings.redis_window,
    )


async def get_auth_rate_limit(request: Request):
    return await check_rate_limit(
        id=request.client.host,
        prefix="auth",
        limit=settings.redis_limit_auth,
        window=settings.redis_window,
    )


async def get_user_rate_limit(user=Depends(get_current_auth_user)):
    return await check_rate_limit(
        id=user.id,
        prefix="user",
        limit=settings.rate_limit_api,
        window=settings.redis_user_window,
    )


async def custom_user_rate_limit(user=Depends(get_current_auth_user)):
    return await check_rate_limit(
        id=user.id,
        prefix="custom",
        limit=5,
        window=60,
    )
