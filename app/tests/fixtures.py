import asyncio
from asyncio import AbstractEventLoop
from typing import Generator

import pytest_asyncio

from app.utils.mongo import db


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db() -> None:
    """
    Clear all collections in the database before each test starts.

    :arg
        - None
    :return
        - None
    """
    for collection_name in await db.list_collection_names():
        await db[collection_name].drop()
