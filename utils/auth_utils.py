import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from pydantic import SecretStr

from core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],  # No length limitations
    default="argon2",
    # Argon2 parameters
    argon2__time_cost=2,
    argon2__memory_cost=65536,
    argon2__parallelism=4,
    deprecated="auto",
)


def encode_jwt(
    payload: dict,
    key: str = settings.private_key_path.read_text(),
    algorithm: str = settings.algorithm,
    expire_minutes: int = settings.access_token_expire,
    expire_timedelta: timedelta | None = None,
):
    jti = str(uuid.uuid4())
    to_encode = deepcopy(payload)
    now = datetime.now(timezone.utc)
    if expire_timedelta is not None:
        exp = now + expire_timedelta
    else:
        exp = now + timedelta(minutes=expire_minutes)

    to_encode.update(iat=now, exp=exp, jti=jti, sub=str(to_encode["id"]))
    to_encode.pop("id", None)

    return jwt.encode(to_encode, key, algorithm)


def decode_jwt(
    jwt_token: str | bytes,
    key: str = settings.public_key_path.read_text(),
    algorithm: str = settings.algorithm,
):
    decoded = jwt.decode(jwt=jwt_token, key=key, algorithms=algorithm)
    return decoded


def hash_pwd(password: str | SecretStr) -> str:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    return pwd_context.hash(password)


def validate_pwd(password: str | SecretStr, hashed_password: str) -> bool:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()

    return pwd_context.verify(password, hashed_password)
