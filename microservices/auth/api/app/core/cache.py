from redis.asyncio import Redis

from app.core.config import settings

redis: Redis | None = None


async def get_redis():
    global redis

    if redis is None:
        redis = Redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=False,
        )
    return redis


async def is_refresh_token_blacklisted(token: str) -> bool:
    redis_ = await get_redis()
    return await redis_.exists(f"blacklisted_refresh:{token}")


async def blacklist_refresh_token(token: str, exp: int) -> None:
    redis_ = await get_redis()
    await redis_.set(f"blacklisted_refresh:{token}", 1, ex=exp)
