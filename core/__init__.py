from task.models.task_model import Task
from user.models.user_model import User

from .setup import async_session_factory


async def get_session():
    async with async_session_factory() as session:
        yield session


__all__ = ["User", "Task"]
