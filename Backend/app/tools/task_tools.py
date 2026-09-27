"""
tools/task_tools.py — The functions the LLM is ALLOWED to call.

This is the agent's "hands". The LLM never touches the database; it can only ask
to call one of these functions with JSON arguments. PydanticAI:

  1. turns each function's name + type hints + docstring into a JSON schema the LLM sees,
  2. validates the arguments the LLM generates against those type hints
     (e.g. task_id must be an int > 0) BEFORE the function runs,
  3. sends the return value back to the LLM as the "tool result".

If validation fails, or a tool raises ModelRetry, the error message is sent back to
the LLM so it can correct itself and try again.
"""
from dataclasses import dataclass
from typing import Annotated

from pydantic import Field, ValidationError
from pydantic_ai import ModelRetry, RunContext
from sqlalchemy.orm import Session

from app.logger import log_step
from app.models.task import TaskStatus
from app.schemas.task import DeleteResult, TaskCreate, TaskOut, TaskUpdate
from app.services import task_service
from app.services.task_service import TaskNotFoundError

# Reusable validated argument type: the LLM must send a positive integer.
TaskId = Annotated[int, Field(gt=0, description="The numeric id of the task")]


@dataclass
class AgentDeps:
    """Things the tools need at run time. Injected per request (dependency injection)."""

    db: Session


def _format_args(**kwargs) -> str:
    return ", ".join(f"{k}={v!r}" for k, v in kwargs.items() if v is not None)


async def create_task(
    ctx: RunContext[AgentDeps],
    title: Annotated[str, Field(min_length=1, max_length=200)],
    description: str | None = None,
) -> TaskOut:
    """Create a new task. New tasks always start with status 'pending'.

    Args:
        title: Short title of the task, e.g. "Learn LangGraph".
        description: Optional longer description.
    """
    log_step("TOOL", f"create_task({_format_args(title=title, description=description)})")
    try:
        data = TaskCreate(title=title, description=description)
    except ValidationError as exc:
        raise ModelRetry(f"Invalid task data: {exc.errors()[0]['msg']}")
    return TaskOut.model_validate(task_service.create_task(ctx.deps.db, data))


async def get_task(ctx: RunContext[AgentDeps], task_id: TaskId) -> TaskOut:
    """Get one task by its id."""
    log_step("TOOL", f"get_task(task_id={task_id})")
    try:
        return TaskOut.model_validate(task_service.get_task(ctx.deps.db, task_id))
    except TaskNotFoundError:
        raise ModelRetry(f"Task {task_id} does not exist. Use list_tasks to find the correct id.")


async def list_tasks(
    ctx: RunContext[AgentDeps],
    status: TaskStatus | None = None,
    title_contains: str | None = None,
) -> list[TaskOut]:
    """List tasks, optionally filtered. Use this to find a task's id from its title.

    Args:
        status: Only return tasks with this status ('pending' or 'completed').
        title_contains: Only return tasks whose title contains this text (case-insensitive).
    """
    log_step("TOOL", f"list_tasks({_format_args(status=status and status.value, title_contains=title_contains)})")
    tasks = task_service.list_tasks(ctx.deps.db, status=status, title_contains=title_contains)
    return [TaskOut.model_validate(t) for t in tasks]


async def update_task(
    ctx: RunContext[AgentDeps],
    task_id: TaskId,
    title: Annotated[str, Field(min_length=1, max_length=200)] | None = None,
    description: str | None = None,
    status: TaskStatus | None = None,
) -> TaskOut:
    """Update a task's title, description and/or status. Only pass the fields that change.

    Args:
        task_id: Id of the task to update.
        title: New title.
        description: New description.
        status: New status: 'pending' or 'completed'.
    """
    log_step("TOOL", f"update_task({_format_args(task_id=task_id, title=title, description=description, status=status and status.value)})")
    try:
        # Only include fields the LLM actually provided.
        changes = {k: v for k, v in {"title": title, "description": description, "status": status}.items() if v is not None}
        data = TaskUpdate(**changes)
    except ValidationError as exc:
        raise ModelRetry(f"Invalid update: {exc.errors()[0]['msg']}")
    try:
        return TaskOut.model_validate(task_service.update_task(ctx.deps.db, task_id, data))
    except TaskNotFoundError:
        raise ModelRetry(f"Task {task_id} does not exist. Use list_tasks to find the correct id.")


async def delete_task(ctx: RunContext[AgentDeps], task_id: TaskId) -> DeleteResult:
    """Permanently delete a task by its id."""
    log_step("TOOL", f"delete_task(task_id={task_id})")
    try:
        return task_service.delete_task(ctx.deps.db, task_id)
    except TaskNotFoundError:
        raise ModelRetry(f"Task {task_id} does not exist. Use list_tasks to find the correct id.")


# The list the agent registers. Adding a new capability = write a function + add it here.
TASK_TOOLS = [create_task, get_task, list_tasks, update_task, delete_task]
