import json
from typing import Dict, List

import aiofiles
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import Task, User
from .setup import Base, async_engine

test_data_path = "test_data.json"


async def get_data() -> Dict[str, List]:
    async with aiofiles.open(test_data_path) as f:
        content = await f.read()
        data = json.loads(content)
    return data


async def recreate_tables() -> Dict[str, str]:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return {"Message": "All tables were recreated"}


async def add_data_into_db(
    session: AsyncSession,
) -> Dict[str, str]:
    data = await get_data()
    if users := data.get("users"):
        session.add_all([User(**user) for user in users])
        await session.flush()

    if tasks := data.get("tasks"):
        session.add_all([Task(**task) for task in tasks])
        await session.flush()

    await session.commit()

    return {"Message": "All test data has been added"}
