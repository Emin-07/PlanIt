import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import Request
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from user.schemas.user_schemas import UserSchema

from .utils import auth_jwt, encode_jwt

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = auth_jwt.access_token_expire,
    expire_timedelta: Optional[timedelta] = None,
):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)

    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: UserSchema) -> str:
    jwt_payload = {**user.model_dump()}
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=auth_jwt.access_token_expire,
    )


def create_refresh_token(user: UserSchema) -> str:
    jwt_payload = {"id": user.id}
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=auth_jwt.refresh_token_expire),
    )


class TokenBlackList:
    def __init__(self):
        self.blacklisted: List[Dict[str, str | datetime]] = []

    def add(self, jti: str, expires_at: datetime):
        self.blacklisted.append({"jti": jti, "exp": expires_at})

    def is_blacklisted(self, jti: str):
        blacklisted_ids = [token["jti"] for token in self.blacklisted]
        return jti in blacklisted_ids

    def _cleanup(self):
        blacklist = deepcopy(self.blacklisted)
        for token in blacklist:
            if token["exp"] < datetime.now(timezone.utc):
                self.blacklisted.remove(token)

    async def start_periodic_cleanup(self, interval_minutes: int = 5):
        while True:
            await asyncio.sleep(60 * interval_minutes)
            self._cleanup


def get_blacklist(request: Request) -> TokenBlackList:
    return request.app.state.blacklist
