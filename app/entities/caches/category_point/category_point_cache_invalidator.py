import asyncio
from abc import ABC, abstractmethod

from app.entities.collections import ShopCollection
from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.category_point.category_point_document import (
    CategoryPointDocument,
)
from app.entities.collections.shop.shop_document import ShopDocument
from app.entities.redis_repositories.category_point_redis_repository import (
    CategoryPointRedisRepository,
)


class CategoryPointCacheInvalidator(ABC):
    def __init__(self, shop: ShopDocument):
        self._shop = shop

    @abstractmethod
    async def invalidate(self) -> None:
        """
        가게 배달 구역 내의 cache 중에서 가게의 카테고리가 없는 cache 를 찾아서 삭제한다.
        """
        pass

    async def _delete_cache(self, point: CategoryPointDocument) -> None:
        """
        반드시 redis 에서 삭제가 성공한 후에 mongodb 에서 삭제해야 합니다.
        mongodb 에서 삭제된 후에 redis 삭제가 실패할 경우, redis 캐시를 다시 찾아서 삭제할 방법이 없기 때문입니다.
        """
        await CategoryPointRedisRepository.delete(point.cache_key)
        await CategoryPointCollection.delete_by_id(point.id)


class ShopCreationCategoryPointCacheInvalidator(CategoryPointCacheInvalidator):
    async def invalidate(self) -> None:
        """
        가게 생성 시, 해당 가게의 모든 category point 캐시를 삭제합니다.
        """
        list_of_point_tuple = await self._get_list_of_point_tuple()
        deleted = set()
        for tp in list_of_point_tuple:
            for point in tp:
                if point.id not in deleted:
                    await self._delete_cache(point)
                    deleted.add(point.id)

    async def _get_list_of_point_tuple(self) -> list[tuple[CategoryPointDocument, ...]]:
        return await asyncio.gather(
            *(
                CategoryPointCollection.get_all_within_polygon_and_code_ne(area.poly, code)
                for area in self._shop.delivery_areas
                for code in self._shop.category_codes
            )
        )


class ShopDeletionCategoryPointCacheInvalidator(CategoryPointCacheInvalidator):
    async def invalidate(self) -> None:
        points_to_delete = await self._get_points_to_delete()
        for point in points_to_delete:
            await self._delete_cache(point)

    async def _get_points_to_delete(self) -> list[CategoryPointDocument]:
        """
        1. 배달구역내에 특정 카테고리가 "있는" 모든 캐시를 가져옵니다.
        2. 각 캐시별로 정말 해당 카테고리의 가게가 하나도 남지 않았는지 확인합니다.
        3. 만약 하나도 남지 않았다면, 결과 리스트에 담아서 리턴합니다. 이후 캐시가 삭제되게 됩니다.
        """
        list_of_point_tuple = await asyncio.gather(
            *(
                CategoryPointCollection.get_all_within_polygon_and_code(area.poly, code)
                for area in self._shop.delivery_areas
                for code in self._shop.category_codes
            )
        )
        id_map = set()
        result = []
        for tp, code in zip(
            list_of_point_tuple,
            (code for _ in self._shop.delivery_areas for code in self._shop.category_codes),
        ):
            for point in tp:
                if point.id not in id_map and not await ShopCollection.exists_by_category_and_point_intersects(
                    code, point.point
                ):
                    id_map.add(point.id)
                    result.append(point)

        return result
