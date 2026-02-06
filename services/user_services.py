from fastapi import Depends, HTTPException, status
from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core import get_session
from models.user_model import User
from schemas.relation_schemas import UserRelSchema
from schemas.user_schemas import UserCreate, UserLogin, UserSchema, UserUpdate
from utils.auth_utils import hash_pwd

# TODO: make default username like, user132121312


async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserSchema:
    new_user = User(
        email=user.email, username=user.username, password=hash_pwd(user.password)
    )
    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return UserSchema.model_validate(new_user)


async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> UserRelSchema:
    user = await session.get(User, user_id, options=[joinedload(User.tasks)])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return UserRelSchema.model_validate(user)


async def get_user_by_email(
    user_email: EmailStr, session: AsyncSession = Depends(get_session)
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
    user_email: EmailStr, session: AsyncSession = Depends(get_session)
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


async def get_users(
    offset: int = 0, limit: int = 5, session: AsyncSession = Depends(get_session)
):
    query = select(User).offset(offset).limit(limit).order_by(User.id)
    res = await session.scalars(query)
    users = res.all()
    return [UserSchema.model_validate(user) for user in users]


async def delete_user_by_id(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with id ({user_id}) found",
        )

    await session.delete(user)
    await session.commit()

    return UserSchema.model_validate(user)


async def change_user(
    user_data: UserUpdate, user_id: int, session: AsyncSession = Depends(get_session)
):
    user_to_change = await session.get(User, user_id)
    user_data_dict = user_data.model_dump(exclude_unset=True)

    for key, val in user_data_dict.items():
        setattr(user_to_change, key, val)

    await session.commit()
    await session.refresh(user_to_change)

    return UserRelSchema.model_validate(user_to_change)
