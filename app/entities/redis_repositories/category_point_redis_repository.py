from typing import Sequence

from app.entities.category.category_codes import CategoryCode
from app.utils.redis import redis


class CategoryPointRedisRepository:
    @classmethod
    async def get(cls, key: str) -> tuple[CategoryCode, ...] | None:
        cached = await redis.get(key)
        if cached is None:
            return None
        if cached == "":
            return ()
        return tuple(CategoryCode(code) for code in cached.split(","))

    @classmethod
    async def set(cls, key: str, codes: Sequence[CategoryCode]) -> None:
        await redis.set(key, ",".join(codes))

    @classmethod
    async def delete(cls, *key: str) -> None:
        await redis.delete(*key)
