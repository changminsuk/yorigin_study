from dataclasses import asdict

import pymongo
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.category_point.category_point_document import (
    CategoryPointDocument,
)
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
from app.utils.mongo import db


class CategoryPointCollection:
    _collection = AsyncIOMotorCollection(db, "category_points")

    @classmethod
    async def set_index(cls) -> None:
        """
        This method is used to set index for the collection.
        """
        await cls._collection.create_index(
            [
                ("point", pymongo.GEOSPHERE),
                ("codes", pymongo.ASCENDING),
            ]
        )
        await cls._collection.create_index("cache_key", unique=True)

    @classmethod
    async def insert_or_replace(
        cls, catch_key: str, point: GeoJsonPoint, codes: tuple[CategoryCode, ...]
    ) -> CategoryPointDocument:
        """
        This method is used to insert or replace the category point document for caching.

        :arg
            - catch_key: str
            - point: GeoJsonPoint
            - codes: tuple[CategoryCode, ...]

        :return
            - CategoryPointDocument
        """
        document_to_insert = {
            "cache_key": catch_key,
            "point": asdict(point),
            "codes": codes,
        }

        try:
            result = await cls._collection.insert_one(document_to_insert)
            _id = result.inserted_id  # = object id
        except DuplicateKeyError:
            inserted_document = await cls._collection.find_one_and_replace(
                {"cache_key": catch_key},
                document_to_insert,
                return_document=ReturnDocument.AFTER,
            )
            _id = inserted_document["_id"]

        return CategoryPointDocument(
            _id=_id,
            cache_key=catch_key,
            point=point,
            codes=codes,
        )

    @classmethod
    async def delete_by_id(cls, _id: ObjectId) -> int:
        """
        This method is used to delete the category point document by id from mongoDB.

        :arg
            - _id: str
        """
        result: DeleteResult = await cls._collection.delete_one({"_id": _id})
        return result.deleted_count

    @classmethod
    async def get_all_within_polygon_and_code_ne(
        cls, polygon: GeoJsonPolygon, code: CategoryCode
    ) -> tuple[CategoryPointDocument, ...]:
        """
        This method is used to get all category point documents within polygon and code not equal.

        :arg
            - polygon: GeoJsonPolygon
            - code: CategoryCode
        :return
            - tuple[CategoryPointDocument, ...]
        """

        return tuple(
            CategoryPointDocument(
                _id=result["_id"],
                cache_key=result["cache_key"],
                codes=tuple(CategoryCode(code) for code in result["codes"]),
                point=GeoJsonPoint(coordinates=result["point"]["coordinates"]),
            )
            for result in await cls._collection.find(
                {
                    "point": {"$geoWithin": {"$geometry": asdict(polygon)}},
                    "codes": {"$ne": code},
                }
            ).to_list(length=None)
        )

    @classmethod
    async def get_all_within_polygon_and_code(
        cls, polygon: GeoJsonPolygon, code: CategoryCode
    ) -> tuple[CategoryPointDocument, ...]:
        """
        This method is used to get all category point documents within polygon and code.

        :arg
            - polygon: GeoJsonPolygon
            - code: CategoryCode
        :return
            - tuple[CategoryPointDocument, ...]
        """

        return tuple(
            CategoryPointDocument(
                _id=result["_id"],
                cache_key=result["cache_key"],
                codes=tuple(CategoryCode(code) for code in result["codes"]),
                point=GeoJsonPoint(coordinates=result["point"]["coordinates"]),
            )
            for result in await cls._collection.find(
                {
                    "point": {"$geoWithin": {"$geometry": asdict(polygon)}},
                    "codes": code.value,
                }
            ).to_list(length=None)
        )
