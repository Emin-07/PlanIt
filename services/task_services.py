from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from core.setup import async_session_factory
from models.task_model import Task
from models.user_model import User
from schemas.relation_schemas import TaskRelSchema
from schemas.task_schemas import TaskBase, TaskSchema, TaskUpdate

from .service import Service

user_model = User  # circular import models fix

task_service: Service = Service(
    model=Task,
    model_options=[selectinload(Task.task_owner)],
    schema=TaskSchema,
    schema_base=TaskBase,
    schema_update=TaskUpdate,
    rel_schema=TaskRelSchema,
)


async def create_task(task_data: TaskBase) -> TaskSchema:
    return await task_service.create_obj(task_data)


async def get_task_by_id(task_id: int) -> TaskRelSchema:
    return await task_service.get_by_id(task_id)


async def get_tasks(offset: int = 0, limit: int = 5) -> List[TaskSchema]:
    return await task_service.get_all(offset, limit)


async def delete_task_by_id(task_id: int) -> TaskSchema:
    return await task_service.delete_obj_by_id(task_id)


async def change_task(task_data: TaskUpdate, task_id: int) -> TaskRelSchema:
    return await task_service.change_obj(task_data, task_id)


async def mark_task_as_complete(task_id: int):
    async with async_session_factory() as session:
        task = await session.get(Task, task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )

        task.is_completed = True
        await session.commit()
        await session.refresh(task)
        return TaskSchema.model_validate(task)
