from bson import ObjectId

from app.dtos.shop.shop_creation_request import ShopCreationRequest
from app.entities.caches.category_point.category_point_cache_invalidator import (
    ShopCreationCategoryPointCacheInvalidator,
    ShopDeletionCategoryPointCacheInvalidator,
)
from app.entities.collections import ShopCollection
from app.entities.collections.shop.shop_document import (
    ShopDeliveryAreaSubDocument,
    ShopDocument,
)
from app.exceptions import ShopNotFoundException


async def create_shop(shop_creation_request: ShopCreationRequest) -> ShopDocument:
    """
    가게 생성은 크게 2 step 으로 이루어집니다.
    1. 가게 정보를 mongoDB 에 저장합니다.
    2. 캐시 삭제
    """
    shop = await ShopCollection.insert_one(
        name=shop_creation_request.name,
        category_codes=list(shop_creation_request.category_codes),
        delivery_areas=[ShopDeliveryAreaSubDocument(poly=area) for area in shop_creation_request.delivery_areas],
    )

    await ShopCreationCategoryPointCacheInvalidator(shop).invalidate()

    return shop


async def delete_shop(shop_id: ObjectId) -> None:
    if not (shop := await ShopCollection.find_by_id(shop_id)):
        raise ShopNotFoundException(f"Shop#{shop_id} is not found")

    await ShopCollection.delete_by_id(shop_id)
    await ShopDeletionCategoryPointCacheInvalidator(shop).invalidate()
