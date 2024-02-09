from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.dtos.category.category_response import CategoryResponse
from app.dtos.category.coordinates_request import CoordinatesRequest
from app.services.category_service import (
    get_distinct_home_categories,
    get_home_categories_one_by_one,
)

router = APIRouter(prefix="/v1/home_categories", tags=["Home Category"], redirect_slashes=False)


@router.get(
    "/distinct",
    description="This method is used to get distinct category codes by point intersects.",
    response_class=ORJSONResponse,
)
async def api_get_categories_distinct(coordinates: Annotated[CoordinatesRequest, Depends()]) -> CategoryResponse:
    """
    This method is used to get distinct category codes by point intersects.
    """
    return CategoryResponse(categories=await get_distinct_home_categories(coordinates.longitude, coordinates.latitude))


@router.get(
    "/one_by_one",
    description="카테고리 하나당 limit 1 짜리 count_documents 쿼리를 날려서 카테고리 목록을 구합니다.",
    response_class=ORJSONResponse,
)
async def api_get_categories_one_by_one(
    coordinates: Annotated[CoordinatesRequest, Depends(CoordinatesRequest)]
) -> CategoryResponse:
    """
    This method is used to get category codes by point intersects.
    """
    return CategoryResponse(
        categories=await get_home_categories_one_by_one(coordinates.longitude, coordinates.latitude)
    )
