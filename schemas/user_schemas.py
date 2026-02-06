from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from models import get_current_utc_time


class UserCreate(BaseModel):
    email: EmailStr = Field(description="User's email address")
    username: str = Field(min_length=3, max_length=50, description="Username")
    password: SecretStr = Field(min_length=4, description="Password (will be hashed)")
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int = Field(description="Unique identifier")
    email: EmailStr = Field(description="User's email, one email per one user")
    username: str = Field(default="user", description="Name of the user")
    created_at: str = Field(
        default=get_current_utc_time(),
        description="Time when user was created",
    )

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class UserPasswordChange(BaseModel):
    current_password: SecretStr
    new_password: SecretStr
