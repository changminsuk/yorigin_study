import dataclasses

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPolygon


@dataclasses.dataclass
class ShopCreationRequest:
    name: str
    category_codes: set[CategoryCode]
    delivery_areas: list[GeoJsonPolygon]
