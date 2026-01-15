from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.setup import Base
from user.models import DateStr, get_current_utc_time, intpk

from ..schemas.task_schemas import PriorityEnum

if TYPE_CHECKING:
    from user.models.user_model import User


class Task(Base):
    id: Mapped[intpk]

    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255), default=None)
    time: Mapped[str] = mapped_column(default=None)
    priority: Mapped[int] = mapped_column(default=PriorityEnum.DEFAULT.value)
    is_completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[DateStr]
    updated_at: Mapped[DateStr] = mapped_column(onupdate=get_current_utc_time)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    task_owner: Mapped["User"] = relationship(back_populates="tasks")
