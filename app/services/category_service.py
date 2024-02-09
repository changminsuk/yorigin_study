from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPoint
from app.entities.collections.shop.shop_collection import ShopCollection


async def get_distinct_home_categories(longitude: float, latitude: float) -> tuple[CategoryCode, ...]:
    """
    This method is used to get distinct category codes by point intersects.

    :arg
        - longitude: float
        - latitude: float
    :return
        - list[CategoryCode]
    """
    return tuple(
        code
        for code in await ShopCollection.get_distinct_category_codes_by_point_intersects(
            GeoJsonPoint(type="Point", coordinates=[longitude, latitude])
        )
    )
