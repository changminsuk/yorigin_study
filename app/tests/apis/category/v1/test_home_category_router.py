from fastapi import status
from httpx import AsyncClient

from app.dtos.category.coordinates_request import CoordinatesRequest
from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPolygon
from app.entities.collections.shop.shop_collection import ShopCollection
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument
from app.main import app


async def test_api_get_categories() -> None:
    # Given
    import asyncio

    await asyncio.gather(
        ShopCollection.insert_one(
            "치킨집",
            [CategoryCode.CHICKEN],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(
                        coordinates=[
                            [
                                [127.005, 37.611],
                                [127.005, 38.611],
                                [128.005, 38.611],
                                [128.005, 37.611],
                                [127.005, 37.611],
                            ]
                        ]
                    ),
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
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/home_categories/distinct", params={"longitude": 127.005, "latitude": 37.611})

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert [elem for elem in response.json()["categories"]] == [CategoryCode.CHICKEN.value]


async def test_api_get_categries_one_by_one_latitude_too_big() -> None:
    # Given
    too_big_latitude = 47.49006

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/v1/home_categories/distinct", params={"longitude": 127.005, "latitude": too_big_latitude}
        )

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_parse_long_latitude() -> None:
    # Given
    too_big_latitude = 47.490061234

    # When
    coordinates_request = CoordinatesRequest(longitude=127.005, latitude=too_big_latitude)

    # Then
    assert coordinates_request.latitude == 47.49006
