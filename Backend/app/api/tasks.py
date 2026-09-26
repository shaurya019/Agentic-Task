"""
api/tasks.py — Plain REST CRUD endpoints (no AI involved).

Why they exist even though the agent does CRUD through tools:
  - the UI's task panel reads GET /tasks to show the real database state,
  - they are handy for testing/debugging in Swagger (http://localhost:8000/docs),
  - they prove that the service layer is reusable: HTTP and the agent share it.
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import TaskStatus
from app.schemas.task import DeleteResult, TaskCreate, TaskOut, TaskUpdate
from app.services import task_service
from app.services.task_service import DatabaseError, TaskNotFoundError

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Path(gt=0): /tasks/0 or /tasks/-5 or /tasks/abc -> automatic 422 "invalid task id".
TaskIdPath = Path(gt=0, description="Task id")


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Task {task_id} not found")


@router.get("", response_model=list[TaskOut])
def list_tasks(status: TaskStatus | None = None, db: Session = Depends(get_db)):
    try:
        return task_service.list_tasks(db, status=status)
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int = TaskIdPath, db: Session = Depends(get_db)):
    try:
        return task_service.get_task(db, task_id)
    except TaskNotFoundError:
        raise _not_found(task_id)


@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    try:
        return task_service.create_task(db, data)
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.put("/{task_id}", response_model=TaskOut)
def update_task(data: TaskUpdate, task_id: int = TaskIdPath, db: Session = Depends(get_db)):
    try:
        return task_service.update_task(db, task_id, data)
    except TaskNotFoundError:
        raise _not_found(task_id)
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.delete("/{task_id}", response_model=DeleteResult)
def delete_task(task_id: int = TaskIdPath, db: Session = Depends(get_db)):
    try:
        return task_service.delete_task(db, task_id)
    except TaskNotFoundError:
        raise _not_found(task_id)
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
