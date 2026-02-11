from typing import List

from fastapi import APIRouter, Depends

from schemas.relation_schemas import UserRelSchema
from schemas.user_schemas import UserSchema
from services.auth_validation import (
    get_current_auth_user,
    get_current_token_payload,
)
from services.user_services import (
    change_user,
    delete_user_by_id,
    get_user_by_email,
    get_user_by_id,
    get_users,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserRelSchema)
async def get_user_by_id_handle(user: UserRelSchema = Depends(get_user_by_id)):
    return user


@router.get("/email/", response_model=UserRelSchema)
async def get_user_by_email_handle(user=Depends(get_user_by_email)):
    return user


@router.get("/", response_model=List[UserSchema])
async def get_users_handle(users: List[UserSchema] = Depends(get_users)):
    return users


@router.delete("/", response_model=UserSchema)
async def delete_user_handle(user: UserSchema = Depends(delete_user_by_id)):
    return user


@router.patch("/", response_model=UserSchema)
async def change_user_handle(user: UserSchema = Depends(change_user)):
    return user


@router.get("/me/")
def auth_person_me(
    payload: dict = Depends(get_current_token_payload),
    user=Depends(get_current_auth_user),
):
    iat = payload.get("iat")
    return {**user.model_dump(), "logged_in_at": iat}
