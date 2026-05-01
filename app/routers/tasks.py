from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import (
    can_manage_project,
    can_view_project,
    get_current_user,
    get_db,
    get_project_membership,
    get_project_or_404,
)
from app.models import GlobalRole, Task, TaskStatus, User
from app.schemas import TaskCreate, TaskOut, TaskUpdate


router = APIRouter(prefix="/api", tags=["Tasks"])


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    if not can_view_project(project, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this project.")

    if payload.assignee_id:
        assignee_membership = get_project_membership(project_id, payload.assignee_id, db)
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a member of this project.",
            )

    task = Task(
        title=payload.title.strip(),
        description=payload.description,
        due_date=payload.due_date,
        project_id=project_id,
        creator_id=current_user.id,
        assignee_id=payload.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
def list_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    if not can_view_project(project, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this project.")
    return db.query(Task).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()


@router.get("/tasks/my", response_model=list[TaskOut])
def list_my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.assignee_id == current_user.id).order_by(Task.created_at.desc()).all()


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    project = get_project_or_404(task.project_id, db)
    if not can_view_project(project, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this task.")

    manager = can_manage_project(project, current_user, db)
    assignee = task.assignee_id == current_user.id
    creator = task.creator_id == current_user.id
    global_admin = current_user.global_role == GlobalRole.ADMIN

    if payload.status is not None:
        if not (manager or assignee or creator or global_admin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update status.")
        task.status = payload.status

    management_fields_requested = any(
        value is not None for value in [payload.title, payload.description, payload.assignee_id, payload.due_date]
    )
    if management_fields_requested and not (manager or global_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project admins can modify task details or assignment.",
        )

    if payload.title is not None:
        task.title = payload.title.strip()
    if payload.description is not None:
        task.description = payload.description
    if payload.assignee_id is not None:
        if payload.assignee_id:
            assignee_membership = get_project_membership(task.project_id, payload.assignee_id, db)
            if not assignee_membership:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be a member of this project.",
                )
        task.assignee_id = payload.assignee_id
    if payload.due_date is not None:
        task.due_date = payload.due_date

    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/overdue", response_model=list[TaskOut])
def list_overdue_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    return (
        db.query(Task)
        .filter(Task.assignee_id == current_user.id, Task.due_date < today, Task.status != TaskStatus.DONE)
        .order_by(Task.due_date.asc())
        .all()
    )

