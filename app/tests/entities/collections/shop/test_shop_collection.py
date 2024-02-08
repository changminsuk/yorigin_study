import asyncio

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
from app.entities.collections.shop.shop_collection import ShopCollection
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument


async def test_shop_insert_one() -> None:
    # Given
    name = "치킨집"
    category_codes = [CategoryCode.CHICKEN]
    delivery_areas = [
        ShopDeliveryAreaSubDocument(
            poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]),
        )
    ]

    # When
    shop = await ShopCollection.insert_one(name, category_codes, delivery_areas)
    results = await ShopCollection._collection.find({}).to_list(None)

    # Then
    assert len(results) == 1
    result = results[0]
    assert result["_id"] == shop.id
    assert result["name"] == shop.name
    assert result["category_codes"] == ["chicken"]
    assert result["delivery_areas"] == [
        {"poly": {"type": "Polygon", "coordinates": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]}}
    ]


async def test_shop_point_intersects() -> None:
    # Given
    await asyncio.gather(
        ShopCollection.insert_one(
            "치킨집",
            [CategoryCode.CHICKEN],
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
    result = await ShopCollection.point_intersects(GeoJsonPoint(coordinates=[5, 5]))

    # Then
    assert len(result) == 1
    assert result[0].name == "치킨집"


async def test_shop_point_intersects_when_it_has_multiple_delivery_area() -> None:
    # Given
    # .gather : 여러개의 코루틴을 병렬 처리
    await asyncio.gather(
        # 코루틴1
        ShopCollection.insert_one(
            "치킨집",
            [CategoryCode.CHICKEN],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]),
                ),
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]),
                ),
            ],
        ),
        # 코루틴2
        ShopCollection.insert_one(
            "피자집",
            [CategoryCode.PIZZA],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]]),
                ),
            ],
        ),
    )

    # When
    result = await ShopCollection.point_intersects(GeoJsonPoint(coordinates=[5, 5]))

    # Then
    assert len(result) == 1
    assert result[0].name == "치킨집"


async def test_shop_get_distinct_category_codes_by_point_intersects() -> None:
    # Given
    await asyncio.gather(
        ShopCollection.insert_one(
            "치킨집",
            [CategoryCode.CHICKEN],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]),
                ),
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]),
                ),
            ],
        ),
        ShopCollection.insert_one(
            "치킨집2",
            [CategoryCode.CHICKEN],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 9], [9, 9], [9, 0], [0, 0]]]),
                ),
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]),
                ),
            ],
        ),
        ShopCollection.insert_one(
            "피자집",
            [CategoryCode.PIZZA],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]]),
                ),
            ],
        ),
        ShopCollection.insert_one(
            "버거집",
            [CategoryCode.BURGER],
            [
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 9], [9, 9], [9, 0], [0, 0]]]),
                ),
            ],
        ),
    )

    # When
    result_codes = await ShopCollection.get_distinct_category_codes_by_point_intersects(
        GeoJsonPoint(coordinates=[5, 5])
    )

    # Then
    assert all(code in result_codes for code in [CategoryCode.CHICKEN, CategoryCode.BURGER])
