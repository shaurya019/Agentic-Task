"""
services/task_service.py — The ONLY place that reads/writes tasks in the database.

Both the REST API (app/api/tasks.py) and the agent tools (app/tools/task_tools.py)
call these functions. The service knows nothing about HTTP or LLMs; it just does CRUD
and raises clear Python exceptions when something is wrong.
"""
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.logger import log_step
from app.models.task import Task, TaskStatus
from app.schemas.task import DeleteResult, TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class DatabaseError(Exception):
    """Wraps low-level SQLAlchemy errors so upper layers get one clear error type."""


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseError(f"Database operation failed: {exc.__class__.__name__}") from exc


def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(title=data.title, description=data.description)
    db.add(task)
    _commit(db)
    db.refresh(task)
    log_step("DATABASE", f"INSERT task {task.id} ({task.title!r})")
    return task


def get_task(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        log_step("DATABASE", f"task {task_id} not found")
        raise TaskNotFoundError(task_id)
    log_step("DATABASE", f"SELECT task {task_id}")
    return task


def list_tasks(db: Session, status: TaskStatus | None = None, title_contains: str | None = None) -> list[Task]:
    query = select(Task).order_by(Task.id)
    if status is not None:
        query = query.where(Task.status == status)
    if title_contains:
        query = query.where(Task.title.ilike(f"%{title_contains}%"))
    try:
        tasks = list(db.scalars(query))
    except SQLAlchemyError as exc:
        raise DatabaseError("Could not read tasks") from exc
    log_step("DATABASE", f"SELECT tasks (status={status and status.value}, title_contains={title_contains!r}) -> {len(tasks)} row(s)")
    return tasks


def update_task(db: Session, task_id: int, data: TaskUpdate) -> Task:
    task = get_task(db, task_id)
    # exclude_unset=True -> only the fields the caller actually sent are changed.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    _commit(db)
    db.refresh(task)
    log_step("DATABASE", f"UPDATE task {task_id}")
    return task


def delete_task(db: Session, task_id: int) -> DeleteResult:
    task = get_task(db, task_id)
    result = DeleteResult(deleted=True, task_id=task.id, title=task.title)
    db.delete(task)
    _commit(db)
    log_step("DATABASE", f"DELETE task {task_id}")
    return result
