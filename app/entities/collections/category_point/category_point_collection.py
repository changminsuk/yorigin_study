from dataclasses import asdict

import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.category_point.category_point_document import (
    CategoryPointDocument,
)
from app.entities.collections.geo_json import GeoJsonPoint
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
