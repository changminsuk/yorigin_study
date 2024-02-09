from app.dtos.shop.shop_creation_request import ShopCreationRequest
from app.entities.category.category_codes import CategoryCode
from app.entities.collections import ShopCollection
from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument
from app.services.shop_service import create_shop


async def test_create_shop_invalidates_point() -> None:
    # Given
    await ShopCollection.insert_one(
        name="sandwich_pizza_shop",
        category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
        delivery_areas=[
            ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]))
        ],
    )
    shop_creation_request = ShopCreationRequest(
        name="chicken_sandwich_shop",
        category_codes={CategoryCode.CHICKEN, CategoryCode.SANDWICH},
        delivery_areas=[GeoJsonPolygon(coordinates=[[[8, 0], [8, 14], [14, 14], [14, 0], [8, 0]]])],
    )
    not_be_removed1 = await CategoryPointCollection.insert_or_replace(
        "3_3",
        GeoJsonPoint(coordinates=[3, 3]),
        (
            CategoryCode.SANDWICH,
            CategoryCode.PIZZA,
        ),
    )
    to_be_removed = await CategoryPointCollection.insert_or_replace(
        "9_9",
        GeoJsonPoint(coordinates=[9, 9]),
        (
            CategoryCode.SANDWICH,
            CategoryCode.PIZZA,
        ),
    )
    not_be_removed2 = await CategoryPointCollection.insert_or_replace(
        "9.2_9.2",
        GeoJsonPoint(coordinates=[9.2, 9.2]),
        (
            CategoryCode.SANDWICH,
            CategoryCode.PIZZA,
            CategoryCode.CHICKEN,
        ),
    )

    # When
    shop = await create_shop(shop_creation_request)

    # Then
    result = await CategoryPointCollection._collection.find({}, {"_id": True}).to_list(None)

    assert len(result) == 2
    ids = [item["_id"] for item in result]
    assert not_be_removed1.id in ids
    assert not_be_removed2.id in ids

    result_shop = await ShopCollection._collection.find_one({"_id": shop.id})
    assert shop.name == result_shop["name"]
