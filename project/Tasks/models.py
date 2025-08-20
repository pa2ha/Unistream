from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Enum
import uuid
from enum import Enum as PyEnum
from Users.models import Base


class TaskStatus(PyEnum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task(Base):
    __tablename__ = 'tasks'

    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.CREATED)

    def __repr__(self):
        return f"<Task(title={self.title}, status={self.status}, id={self.id})>"
    