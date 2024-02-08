from dataclasses import asdict
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
from app.entities.collections.shop.shop_document import (
    ShopDeliveryAreaSubDocument,
    ShopDocument,
)
from app.utils.mongo import db


class ShopCollection:
    _collection = AsyncIOMotorCollection(db, "shops")

    @classmethod
    async def point_intersects(cls, point: GeoJsonPoint) -> list[ShopDocument]:
        return [
            cls._parse(result)
            for result in await cls._collection.find(
                {"delivery_areas.poly": {"$geoIntersects": {"$geometry": asdict(point)}}}
            ).to_list(None)
        ]

    """
    This method is used to get distinct category codes by point intersects. (중복 제거)
    """

    @classmethod
    async def get_distinct_category_codes_by_point_intersects(cls, point: GeoJsonPoint) -> list[CategoryCode]:
        return [
            CategoryCode(category_code)
            for category_code in await cls._collection.distinct(
                "category_codes",  # 중복 제거를 원하는 필드명
                {"delivery_areas.poly": {"$geoIntersects": {"$geometry": asdict(point)}}},  # 조건
            )
        ]

    @classmethod
    async def insert_one(
        cls, name: str, category_codes: list[CategoryCode], delivery_areas: list[ShopDeliveryAreaSubDocument]
    ) -> ShopDocument:
        result = await cls._collection.insert_one(
            {
                "name": name,
                "category_codes": category_codes,
                "delivery_areas": [asdict(delivery_area) for delivery_area in delivery_areas],
            }
        )

        return ShopDocument(
            _id=result.inserted_id,
            name=name,
            category_codes=category_codes,
            delivery_areas=delivery_areas,
        )

    @classmethod
    def _parse(cls, result: dict[str, Any]) -> ShopDocument:
        return ShopDocument(
            _id=result["_id"],
            name=result["name"],
            delivery_areas=[
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=area["poly"]["coordinates"]),
                )
                for area in result["delivery_areas"]
            ],
            category_codes=[CategoryCode(category_code) for category_code in result["category_codes"]],
        )
