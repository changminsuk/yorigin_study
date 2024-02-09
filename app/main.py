from fastapi import FastAPI

from app.apis.category.v1.home_category_router import router as home_category_router
from app.tests.entities.collections import set_indexes

app = FastAPI()

app.include_router(home_category_router)


@app.on_event("startup")
async def on_startup() -> None:
    """
    FastAPI app 이 실행되기 전에 실행되는 startup event handler 를 등록합니다.
    """
    await set_indexes()
