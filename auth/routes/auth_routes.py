from fastapi import APIRouter, Depends, Request

from user.schemas.user_schemas import UserSchema

from ..auth_schema import TokenInfo
from ..services.validation import (
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload,
    validate_auth_user,
)
from ..utils.helper import (
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
    blacklist.add(jti=payload["jti"], expires_at=payload["exp"])

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/check/")
def auth_person_check(
    payload: dict = Depends(get_current_token_payload),
    user=Depends(get_current_auth_user),
):
    iat = payload.get("iat")
    return {**user.model_dump(), "logged_in_at": iat}
