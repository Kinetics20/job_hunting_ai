from typing import Any

from pydantic import EmailStr
from redis.asyncio import Redis

from app.core.config import settings


async def is_blocked(redis: Redis, key: str) -> bool:
    return await redis.exists(f"login_blocked:{key}")

async def record_failed_login(
    redis: Redis,
    key: str,
    max_attempts: int,
    block_time: int
) -> None:
    attempts_key = f"login_attempts:{key}"
    blocked_key = f"login_blocked:{key}"
    attempts = await redis.incr(attempts_key)
    if attempts == 1:
        await redis.expire(attempts_key, block_time)
    if attempts >= max_attempts:
        await redis.set(blocked_key, 1, ex=block_time)
        await redis.delete(attempts_key)

async def reset_login_attempts(redis: Redis, key: str) -> None:
    await redis.delete(f"login_attempts:{key}")
    await redis.delete(f"login_blocked:{key}")


async def is_login_blocked(redis: Redis, email: EmailStr) -> bool:
    return await is_blocked(redis, str(email))

async def record_failed_login_email(redis: Redis, email: EmailStr) -> None:
    await record_failed_login(
        redis,
        str(email),
        settings.MAX_LOGIN_ATTEMPTS,
        settings.BLOCK_TIME_SECONDS
    )

async def reset_login_attempts_email(redis: Redis, email: EmailStr) -> None:
    await reset_login_attempts(redis, str(email))


async def is_ip_blocked(redis: Redis, ip: str) -> bool:
    return await is_blocked(redis, ip)

async def record_failed_login_ip(redis: Redis, ip: str) -> None:
    await record_failed_login(
        redis,
        ip,
        settings.MAX_LOGIN_ATTEMPTS_PER_IP,
        settings.BLOCK_TIME_IP_SECONDS
    )

async def reset_login_attempts_ip(redis: Redis, ip: str) -> None:
    await reset_login_attempts(redis, ip)