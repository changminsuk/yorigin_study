from bson import ObjectId
from fastapi import status
from httpx import AsyncClient

from app.entities.caches.category_point.category_point_cache import CategoryPointCache
from app.entities.category.category_codes import CategoryCode
from app.entities.collections import CategoryPointCollection, ShopCollection
from app.entities.collections.geo_json import GeoJsonPolygon
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument
from app.main import app
from app.services.category_service import get_home_categories_cached
from app.services.shop_service import delete_shop
from app.utils.redis import redis


async def test_api_create_shop() -> None:
    # Given
    coordinates = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]
    request_body = {
        "name": "test_name",
        "category_codes": [CategoryCode.CHICKEN.value],
        "delivery_areas": [{"type": "Polygon", "coordinates": coordinates}],
    }

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/shops",
            json=request_body,
        )

    # Then
    assert response.status_code == status.HTTP_200_OK
    shop = await ShopCollection._collection.find_one({"_id": ObjectId(response.json()["id"])})
    assert shop is not None
    assert shop["category_codes"] == request_body["category_codes"]
    assert len(shop["delivery_areas"]) == 1
    assert shop["delivery_areas"][0]["poly"]["coordinates"] == coordinates


async def test_one_shop_deleted_then_cache_should_be_deleted() -> None:
    # Given
    shop_to_be_removed = await ShopCollection.insert_one(
        name="sandwich_pizza_shop",
        category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
        delivery_areas=[
            ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]))
        ],
    )
    await ShopCollection.insert_one(
        name="sandwich_pizza_shop2",
        category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
        delivery_areas=[
            ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=[[[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]]]))
        ],
    )
    await get_home_categories_cached(3.0, 3.0)
    cache_key_to_be_removed = CategoryPointCache(3.0, 3.0).cache_key
    await get_home_categories_cached(9.0, 9.0)
    cache_key_not_to_be_removed = CategoryPointCache(9.0, 9.0).cache_key

    # When
    await delete_shop(shop_to_be_removed.id)

    # Then
    result = await CategoryPointCollection._collection.find({}).to_list(None)
    assert len(result) == 1
    assert result[0]["cache_key"] == cache_key_not_to_be_removed
    assert await redis.get(cache_key_to_be_removed) is None
    assert await redis.get(cache_key_not_to_be_removed) == "pizza,sandwich"


async def test_api_delete_shop() -> None:
    # Given
    shop = await ShopCollection.insert_one(
        name="sandwich_pizza_shop",
        category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
        delivery_areas=[
            ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]))
        ],
    )
    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/v1/shops/{shop.id}",
        )

    # Then
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await ShopCollection.find_by_id(shop.id) is None


async def test_api_delete_shop_when_delete_non_existing_shop_then_it_returns_400() -> None:
    # Given
    non_existing_shop_id = "64622be98d618c0d271a0238"

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/v1/shops/{non_existing_shop_id}",
        )

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_api_delete_shop_when_delete_invalid_shop_then_it_returns_422() -> None:
    # Given
    invalid_shop_id = "invalid_id"

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/v1/shops/{invalid_shop_id}",
        )

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
