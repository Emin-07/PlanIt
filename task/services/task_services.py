from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core import get_session
from core.relation_schemas import TaskRelSchema

from ..models.task_model import Task
from ..schemas.task_schemas import TaskBase, TaskSchema, TaskUpdate


async def create_task(
    task: TaskBase, session: AsyncSession = Depends(get_session)
) -> TaskSchema:
    new_task = Task(**task)
    session.add(new_task)

    await session.commit()
    await session.refresh(new_task)

    return TaskSchema.model_validate(new_task)


async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id, options=[selectinload(Task.task_owner)])

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No task with id ({task_id}) found",
        )
    return TaskRelSchema.model_validate(task)


async def get_tasks(
    offset: int, limit: int, session: AsyncSession = Depends(get_session)
) -> List[TaskSchema]:
    query = select(Task).offset(offset).limit(limit).order_by(Task.id)
    res = await session.scalars(query)
    tasks = res.all()
    return [TaskSchema.model_validate(task) for task in tasks]


# async def get_tasks_by_user(
#     user_email: Optional[str] = None,
#     user_id: Optional[int] = None,
#     session: AsyncSession = Depends(get_session),
# ) -> List[TaskSchema]:
#     if user_id is not None:
#         query = select(Task).where(Task.user_id == user_id)
#         res = await session.execute(query)
#         tasks = res.all()
#     elif user_email is not None:
#         query = select(User).where(User.email == user_email)
#         res = await session.execute(query)
#         tasks = res.all()
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Neither email nor id were provided, tasks could not be found :(",
#         )

#     validated_tasks = [TaskSchema.model_validate(task) for task in tasks]
#     return validated_tasks


async def delete_task_by_id(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No task with id ({task_id}) found",
        )

    session.delete(task)
    await session.commit()

    return TaskSchema.model_validate(task)


async def change_task(
    task_data: TaskUpdate, task_id: int, session: AsyncSession = Depends(get_session)
):
    task_to_change = await session.get(Task, task_id)
    task_data_dict = task_data.model_dump(exclude_unset=True)

    for key, val in task_data_dict.items():
        setattr(task_to_change, key, val)

    await session.commit()
    await session.refresh(task_to_change)

    return TaskRelSchema.model_validate(task_to_change)
