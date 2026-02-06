import json
from typing import Dict, List

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

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


def get_data_sync() -> Dict[str, List]:
    with open(test_data_path) as f:
        content = f.read()
        data = json.loads(content)
    return data


def add_data_into_db_sync(data: dict, session: Session) -> None:
    try:
        if users := data.get("users"):
            session.bulk_insert_mappings(User, users)
            session.flush()

            users_from_db = session.query(User).all()
            user_id_mapping = {i + 1: u.id for i, u in enumerate(users_from_db)}

        if tasks := data.get("tasks"):
            fixed_tasks = []
            for task in tasks:
                expected_user_id = task["user_id"]
                actual_user_id = user_id_mapping.get(expected_user_id)

                if actual_user_id is None:
                    print(f"WARNING: No user found for ID {expected_user_id}")
                    continue

                task["user_id"] = actual_user_id
                fixed_tasks.append(task)

            session.bulk_insert_mappings(Task, fixed_tasks)
            session.flush()
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"ERROR: {e}")
        raise
