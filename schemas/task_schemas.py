from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models import get_current_utc_time


class PriorityEnum(Enum):
    DEFAULT = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class TaskBase(BaseModel):
    title: str = Field(description="Title of the task")
    description: Optional[str] = Field(
        default=None, description="Details about the task"
    )
    time: Optional[str] = Field(
        default=None, description="Time when the task is supposed to be done "
    )
    priority: int = Field(
        default=PriorityEnum.DEFAULT.value, description="Priority of the task"
    )
    is_completed: bool = Field(
        default=False,
        description="Status of the task which shows, whether the task is completed or not",
    )
    created_at: str = Field(
        default=get_current_utc_time(), description="Date of when the task was created"
    )
    updated_at: str = Field(
        default=get_current_utc_time(),
        description="Date of when the task was last updated",
    )
    user_id: int = Field(description="Id of the user this task belongs to")

    model_config = ConfigDict(from_attributes=True)


class TaskSchema(TaskBase):
    id: int = Field(description="Unique identifier")


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time: Optional[str] = None
    priority: Optional[int] = None
    is_completed: Optional[bool] = None
    created_at: Optional[str] = None
