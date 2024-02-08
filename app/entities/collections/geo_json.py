import dataclasses
from typing import Literal, Sequence


@dataclasses.dataclass(kw_only=True)
class GeoJsonPolygon:
    coordinates: Sequence[Sequence[Sequence[float]]]
    type: Literal["Polygon"] = "Polygon"


@dataclasses.dataclass(kw_only=True)
class GeoJsonPoint:
    coordinates: Sequence[float]
    type: Literal["Point"] = "Point"
