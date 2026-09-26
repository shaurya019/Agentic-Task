"""
models/task.py — The SQLAlchemy ORM model: what a row in the `tasks` table looks like.

Models describe the DATABASE shape. Schemas (app/schemas) describe the API shape.
Keeping them separate means the DB can change without breaking the API contract.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
