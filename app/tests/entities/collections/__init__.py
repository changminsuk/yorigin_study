from app.entities.collections.shop.shop_collection import ShopCollection


async def set_indexes() -> None:
    await ShopCollection.set_index()
