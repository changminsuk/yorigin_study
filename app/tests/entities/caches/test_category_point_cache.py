import asyncio

from app.entities.caches.category_point.category_point_cache import CategoryPointCache
from app.entities.category.category_codes import CategoryCode
from app.entities.collections import ShopCollection
from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.geo_json import GeoJsonPolygon
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument
from app.utils.redis import redis


async def test_category_cache_create_category_point() -> None:
    # Given
    category_point_cache = CategoryPointCache(1.23, 4.56)

    await asyncio.gather(
        ShopCollection.insert_one(
            "치킨 버거집",
            [CategoryCode.CHICKEN, CategoryCode.BURGER],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]),
                )
            ],
        ),
        ShopCollection.insert_one(
            "피자집",
            [CategoryCode.PIZZA],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]]),
                )
            ],
        ),
    )

    # When
    await category_point_cache.get_codes()
    point = await CategoryPointCollection._collection.find_one(filter={"cache_key": category_point_cache.cache_key})

    # Then
    assert point["cache_key"] == category_point_cache.cache_key
    assert set(point["codes"]) == {CategoryCode.CHICKEN.value, CategoryCode.BURGER.value}
    redis_point = await redis.get(category_point_cache.cache_key)
    assert redis_point
    assert set(redis_point.split(",")) == {"chicken", "burger"}


async def test_category_cache_when_no_categories_then_it_creates_empty_category_point() -> None:
    # Given
    category_point_cache = CategoryPointCache(1.23, 4.56)

    # When
    codes = await category_point_cache.get_codes()

    # Then
    point = await CategoryPointCollection._collection.find_one(filter={"cache_key": category_point_cache.cache_key})
    assert codes == tuple()
    assert point["cache_key"] == category_point_cache.cache_key
    assert point["codes"] == []
    assert await redis.get(category_point_cache.cache_key) == ""
