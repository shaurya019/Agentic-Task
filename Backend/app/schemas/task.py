"""
schemas/task.py — Pydantic models that VALIDATE data coming in and SHAPE data going out.

They are used by BOTH the REST endpoints and the agent tools, so a task created
through the chat is validated by exactly the same rules as one created via POST /tasks.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Learn Agentic AI"])
    description: str | None = Field(default=None, max_length=1000)
    
    @field_validator("title")
    @classmethod
    def title_not_blank(cls,value):
        value = value.strip()
        if not value:
            raise ValueError("title cannot be blank")
        return value
    
class TaskUpdate(BaseModel):
    """Every field is optional, but at least one must be provided."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None
    
    @model_validator(mode="after")
    def at_least_one_field(self) -> "TaskUpdate":
        if self.title is None and self.description is None and self.status is None:
            raise ValueError("provide at least one of: title, description, status")
        return self
    
class TaskOut(BaseModel):
    # from_attributes=True lets Pydantic read directly from a SQLAlchemy object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class DeleteResult(BaseModel):
    deleted: bool
    task_id: int
    title: str