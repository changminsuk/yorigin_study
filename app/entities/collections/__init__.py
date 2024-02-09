from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.shop.shop_collection import ShopCollection


async def set_indexes() -> None:
    await CategoryPointCollection.set_index()
    await ShopCollection.set_index()
