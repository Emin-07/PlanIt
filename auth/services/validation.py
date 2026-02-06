from datetime import datetime, timezone

import jwt
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import EmailStr

from core import get_session
from user.schemas.user_schemas import UserLogin
from user.services.user_services import (
    get_user_by_email,
    get_user_by_email_for_login,
    get_user_by_id,
)

from ..utils.helper import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
    http_bearer,
)
from ..utils.utils import decode_jwt, validate_pwd


async def validate_auth_user(
    email: EmailStr = Form(), password: str = Form(), session=Depends(get_session)
):
    user_login: UserLogin = await get_user_by_email_for_login(email, session)
    if user_login is not None:
        if validate_pwd(password, user_login.password.get_secret_value()):
            return await get_user_by_email(email, session)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid password or email, {email}, {password}, {user_login.password.get_secret_value()}, {validate_pwd(password=password, hashed_password=user_login.password.get_secret_value())}",
    )


async def get_current_token_payload(
    creds: HTTPAuthorizationCredentials = Depends(http_bearer),
):

    token = creds.credentials
    try:
        payload = decode_jwt(token)
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Token : {e}",
        )
    return payload


async def validate_blacklisted_token(payload: dict, request: Request):
    blacklist = request.app.state.blacklist
    if blacklist.is_blacklisted(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your token is blacklisted use newer token, or log in to get another one",
        )
    return True


async def validate_suspicious_token(payload: dict, request: Request):
    blacklist = request.app.state.blacklist
    earliest_token_expiry: int | None = blacklist.is_suspicious(payload["sub"])
    if earliest_token_expiry:
        earliest_token_expiry_dt = datetime.fromtimestamp(
            earliest_token_expiry, tz=timezone.utc
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You've been temporarily banned due to having suspicious activity, you can receive new refresh token either by logging in or waiting until {earliest_token_expiry_dt}",
        )
    return True


async def validate_token_type(payload: dict, expected_token_type: str):
    token_type = payload.get(TOKEN_TYPE_FIELD)
    if token_type != expected_token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type : {token_type!r}, when expected type is {expected_token_type!r}",
        )
    return True


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        request: Request,
        payload: dict = Depends(get_current_token_payload),
        session=Depends(get_session),
    ):
        await validate_token_type(payload, self.token_type)
        await validate_blacklisted_token(payload, request)
        await validate_suspicious_token(payload, request)
        return await get_user_by_id(int(payload.get("sub")), session)


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)
