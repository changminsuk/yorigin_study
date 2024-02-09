from app.entities.category.category_codes import CategoryCode
from app.entities.redis_repositories.category_point_redis_repository import (
    CategoryPointRedisRepository,
)


async def test_category_point_set_and_get() -> None:
    # Given
    key = "1_2"
    codes = (CategoryCode.CHICKEN, CategoryCode.PIZZA)

    # When
    await CategoryPointRedisRepository.set(key, codes)

    # Then
    assert await CategoryPointRedisRepository.get(key) == codes


async def test_category_point_delete() -> None:
    # Given
    key = "1_2"
    codes = (CategoryCode.CHICKEN, CategoryCode.PIZZA)
    await CategoryPointRedisRepository.set(key, codes)

    # When
    await CategoryPointRedisRepository.delete(key)

    # Then
    assert await CategoryPointRedisRepository.get(key) is None


async def test_category_point_set_and_get_empty() -> None:
    # Given
    key = "1_2"
    codes = ()

    # When
    await CategoryPointRedisRepository.set(key, codes)

    # Then
    assert await CategoryPointRedisRepository.get(key) == codes
