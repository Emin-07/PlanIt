from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.setup import Base

from . import DateStr, intpk

if TYPE_CHECKING:
    from .task_model import Task


class User(Base):
    id: Mapped[intpk]

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    password: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[DateStr]

    tasks: Mapped[List["Task"]] = relationship(
        back_populates="task_owner", cascade="all, delete-orphan"
    )
