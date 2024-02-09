from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import Response

from app.dtos.shop.shop_creation_response import ShopCreationResponse
from app.exceptions import ShopNotFoundException
from app.services.shop_service import ShopCreationRequest, create_shop, delete_shop

router = APIRouter(prefix="/v1/shops", tags=["Shop"], redirect_slashes=False)


@router.post(
    "",
    description="shop 을 생성합니다.",
    response_class=ORJSONResponse,
)
async def api_create_shop(shop_creation_request: ShopCreationRequest) -> ShopCreationResponse:
    shop = await create_shop(shop_creation_request)
    return ShopCreationResponse(id=str(shop.id))


@router.delete(
    "/{shop_id}", description="shop 을 삭제합니다.", response_class=Response, status_code=status.HTTP_204_NO_CONTENT
)
async def api_delete_shop(shop_id: str) -> None:
    try:
        await delete_shop(ObjectId(shop_id))
    except ShopNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.response_message},
        )
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "id should be valid bson object id"},
        )
