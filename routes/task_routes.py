from typing import List

from fastapi import APIRouter, Depends, status

from schemas.relation_schemas import TaskRelSchema
from schemas.task_schemas import TaskSchema
from services.task_services import (
    change_task,
    create_task,
    delete_task_by_id,
    get_task_by_id,
    get_tasks,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{id}", response_model=TaskRelSchema)
async def get_task_handle(id: int):
    task = await get_task_by_id(id)
    return task


@router.get("/", response_model=List[TaskSchema])
async def get_tasks_handle(tasks: List[TaskSchema] = Depends(get_tasks)):
    return tasks


@router.delete("/", response_model=TaskSchema)
async def delete_task_handle(task: TaskSchema = Depends(delete_task_by_id)):
    return task


@router.patch("/", response_model=TaskSchema)
async def change_task_handle(task: TaskSchema = Depends(change_task)):
    return task


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task_handle(task: TaskSchema = Depends(create_task)):
    return task


@router.post("/{id}/complete", response_model=TaskSchema)
async def mark_task_complete_handle(id: int):
    from services.task_services import mark_task_as_complete

    return await mark_task_as_complete(id)
