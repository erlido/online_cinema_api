import functools

import pydantic
from aioredis import Redis
from fastapi import Request

from src.core.config import settings
from src.models.person import Person

redis: Redis | None = None


async def get_redis() -> Redis | None:
    """Function for injecting dependency for Redis"""
    return redis


def redis_cache(
        model: settings.CINEMA_MODEL,
        expired: int = 60,
):
    """A decorator for caching."""

    def wrap(fn):
        @functools.wraps(fn)
        async def decorated(request: Request, **kwargs):
            key = hash(request.url.path + "?" + str(request.query_params))
            data = await _from_redis_cache(model, key)

            if data:
                return data

            data = await fn(request, **kwargs)

            if data is None:
                return None

            await _to_redis_cache(key, data, expire_time=expired)
            return data

        return decorated

    return wrap


async def _from_redis_cache(model_cls, key: int):
    """Get data from Redis."""
    data = await redis.get(key)

    if not data:
        return None

    try:
        return pydantic.parse_raw_as(list[model_cls], data)
    except pydantic.ValidationError:
        return model_cls.parse_raw(data)


async def _to_redis_cache(key: int,
                          data: pydantic.BaseModel | list[pydantic.BaseModel],
                          expire_time: int):
    """Store cache to Redis."""
    if type(data) is list:
        if data and isinstance(data[0], Person):
            serialized_objs = [x.json().replace('full_name', 'name')
                               for x in data]
        else:
            serialized_objs = [x.json() for x in data]
        serialized_str = ",".join(serialized_objs)
        json_data = f"[{serialized_str}]"
    else:
        json_data = data.json()
        if isinstance(data, Person):
            json_data = json_data.replace('full_name', 'name')
    await redis.set(key, json_data, expire=expire_time)
