import dataclasses

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.base_document import BaseDocument
from app.entities.collections.geo_json import GeoJsonPoint


@dataclasses.dataclass
class CategoryPointDocument(BaseDocument):
    """
    This class is used to define the category point document.
    """

    cache_key: str  # f'{longitude}_{latitude}'
    codes: tuple[CategoryCode, ...]  # 특정 좌표에 어떤 카테고리가 있는지
    point: GeoJsonPoint  # 좌표
