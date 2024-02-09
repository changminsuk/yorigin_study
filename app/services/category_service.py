import asyncio

from app.entities.category.categories import CATEGORIES, Category
from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPoint
from app.entities.collections.shop.shop_collection import ShopCollection


async def get_distinct_home_categories(longitude: float, latitude: float) -> tuple[Category, ...]:
    """
    This method is used to get distinct category codes by point intersects.

    :arg
        - longitude: float
        - latitude: float
    :return
        - list[CategoryCode]
    """
    return tuple(
        CATEGORIES[code]
        for code in await ShopCollection.get_distinct_category_codes_by_point_intersects(
            GeoJsonPoint(type="Point", coordinates=[longitude, latitude])
        )
    )


async def get_home_categories_one_by_one(longitude: float, latitude: float) -> tuple[Category, ...]:
    """
    This method is used to get category codes by point intersects.

    :arg
        - longitude: float
        - latitude: float
    :return
        - list[CategoryCode]
    """
    li = [
        ShopCollection.exists_by_category_and_point_intersects(
            code, GeoJsonPoint(type="Point", coordinates=[longitude, latitude])
        )
        for code in CategoryCode
    ]
    return tuple(CATEGORIES[code] for code, exists in zip(CategoryCode, await asyncio.gather(*li)) if exists)
