from dataclasses import asdict
from typing import Any, cast

import pymongo
from bson import ObjectId
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
    async def set_index(cls) -> None:
        """
        This method is used to set index for the collection.
        폴리곤 + 카테고리 코드 복합 인덱스를 설정합니다.
        """
        await cls._collection.create_index(
            [
                ("delivery_areas.poly", pymongo.GEOSPHERE),
                ("category_codes", pymongo.ASCENDING),
            ]
        )

    @classmethod
    async def exists_by_category_and_point_intersects(cls, category_code: CategoryCode, point: GeoJsonPoint) -> bool:
        """
        This method is used to check if the shop exists by category and point intersects.

        :arg
            - category_code: CategoryCode
            - point: GeoJsonPoint
        :return
            - bool
        """
        cnt = await cls._collection.count_documents(
            {
                "category_codes": category_code,
                "delivery_areas.poly": {"$geoIntersects": {"$geometry": asdict(point)}},
            },
            limit=1,
        )
        return bool(cnt)

    @classmethod
    async def point_intersects(cls, point: GeoJsonPoint) -> list[ShopDocument]:
        return [
            cls._parse(result)
            for result in await cls._collection.find(
                {"delivery_areas.poly": {"$geoIntersects": {"$geometry": asdict(point)}}}
            ).to_list(None)
        ]

    @classmethod
    async def get_distinct_category_codes_by_point_intersects(cls, point: GeoJsonPoint) -> list[CategoryCode]:
        """
        This method is used to get distinct category codes by point intersects. (중복 제거)

        :arg
            - point: GeoJsonPoint
        :return
            - list[CategoryCode]
        """
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
    async def find_by_id(cls, object_id: ObjectId) -> ShopDocument | None:
        result = await cls._collection.find_one({"_id": object_id})
        return cls._parse(result) if result else None

    @classmethod
    async def delete_by_id(cls, object_id: ObjectId) -> int:
        result = await cls._collection.delete_one({"_id": object_id})
        return cast(int, result.deleted_count)

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
