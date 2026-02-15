from fastapi import APIRouter, Depends, Request
from pydantic import EmailStr

from schemas.auth_schema import TokenInfo
from schemas.user_schemas import UserSchema
from services.auth_validation import (
    get_current_auth_user_for_refresh,
    get_current_token_payload,
    validate_auth_user,
)
from utils.auth_helper import (
    create_access_token,
    create_refresh_token,
    http_bearer,
)

router = APIRouter(tags=["jwt"], prefix="/jwt", dependencies=[Depends(http_bearer)])


@router.post("/login/", response_model=TokenInfo, response_model_exclude_none=True)
def auth_user_issue_jwt_access(user: UserSchema = Depends(validate_auth_user)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
def auth_user_issue_jwt_refresh(
    request: Request,
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
    payload: dict = Depends(get_current_token_payload),
):
    blacklist = request.app.state.blacklist
    blacklist.add(jti=payload["jti"], expires_at=payload["exp"], sub=payload["sub"])

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout/")
def auth_user_logout(
    request: Request,
    payload: dict = Depends(get_current_token_payload),
):
    blacklist = request.app.state.blacklist
    blacklist.add(jti=payload["jti"], expires_at=payload["exp"], sub=payload["sub"])
    return {"detail": "Successfully logged out"}
