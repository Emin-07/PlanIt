import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi import Request
from fastapi.security import (
    HTTPBearer,
)

from user.schemas.user_schemas import UserSchema

from .utils import auth_jwt, encode_jwt

http_bearer = HTTPBearer(auto_error=False)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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
        expire_timedelta=timedelta(days=auth_jwt.refresh_token_expire_web),
        # expire_timedelta=timedelta(minutes=2),
    )


class TokenBlackList:
    def __init__(self):
        self.jti_to_expiry_blacklist: Dict[str, datetime] = {}
        self.jti_to_user_blacklist: Dict[str, str] = {}

    def add(self, jti: str, expires_at: datetime, sub: str):
        self.jti_to_expiry_blacklist[jti] = expires_at
        self.jti_to_user_blacklist[jti] = sub

    def is_blacklisted(self, jti: str):
        return jti in self.jti_to_expiry_blacklist

    # TODO: IP Change Detection
    def is_suspicious(self, sub: str):
        user_tokens_to_expiry = {}
        for jti, user_id in self.jti_to_user_blacklist.items():
            if user_id == sub:
                user_tokens_to_expiry[jti] = self.jti_to_expiry_blacklist[jti]

        if len(user_tokens_to_expiry) > 7:
            earliest_token_expiry = sorted(
                user_tokens_to_expiry.items(), key=lambda item: item[1]
            )[0][1]
            return earliest_token_expiry
        print(user_tokens_to_expiry)
        return False

    def _cleanup(self):
        to_delete_jti = []
        for jti, expiry in self.jti_to_expiry_blacklist.items():
            expiry_dt = datetime.fromtimestamp(expiry, tz=timezone.utc)
            if expiry_dt < datetime.now(timezone.utc):
                to_delete_jti.append(jti)

        for jti in to_delete_jti:
            del self.jti_to_expiry_blacklist[jti]
            del self.jti_to_user_blacklist[jti]

    async def start_periodic_cleanup(self, interval_minutes: int = 5):
        while True:
            print(f"[{datetime.now()}] Cleanup running...")
            await asyncio.sleep(60 * interval_minutes)
            self._cleanup()
            print(f"[{datetime.now()}] Cleanup finished...")


def get_blacklist(request: Request) -> TokenBlackList:
    return request.app.state.blacklist
