# TODO: make default username like, user132121312
from typing import List

from fastapi import Depends, HTTPException, status
from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.setup import get_db
from models.task_model import Task  # Add this import
from models.user_model import User
from schemas.relation_schemas import UserRelSchema
from schemas.user_schemas import UserCreate, UserLogin, UserSchema, UserUpdate

from .service import Service

task_model = Task  # circular import models fix

user_service: Service = Service(
    model=User,
    model_options=[joinedload(User.tasks)],
    schema=UserSchema,
    schema_base=UserCreate,
    schema_update=UserUpdate,
    rel_schema=UserRelSchema,
)


async def create_user(user_data: UserCreate) -> UserSchema:
    return await user_service.create_obj(user_data)


async def get_user_by_id(user_id: int) -> UserRelSchema:
    return await user_service.get_by_id(user_id)


async def get_users(offset: int = 0, limit: int = 5) -> List[UserSchema]:
    return await user_service.get_all(offset, limit)


async def delete_user_by_id(user_id: int) -> UserSchema:
    return await user_service.delete_obj_by_id(user_id)


async def change_user(user_data: UserUpdate, user_id: int) -> UserRelSchema:
    return await user_service.change_obj(user_data, user_id)


async def get_user_by_email(
    user_email: EmailStr, session: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == user_email).options(joinedload(User.tasks))
    res = await session.scalars(query)

    user = res.unique().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {user_email} not found",
        )

    return UserRelSchema.model_validate(user)


async def get_user_by_email_for_login(
    user_email: EmailStr, session: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == user_email)
    res = await session.scalars(query)

    user = res.unique().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {user_email} not found",
        )

    return UserLogin(email=user.email, password=SecretStr(user.password))
