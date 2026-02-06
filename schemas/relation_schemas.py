from typing import List

from .task_schemas import TaskSchema
from .user_schemas import UserSchema


class TaskRelSchema(TaskSchema):
    task_owner: "UserSchema"


class UserRelSchema(UserSchema):
    tasks: List["TaskSchema"] = []
