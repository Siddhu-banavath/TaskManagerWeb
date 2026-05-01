from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import GlobalRole, ProjectMember, Task, TaskStatus, User
from app.schemas import DashboardSummary


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task_query = db.query(Task)
    if current_user.global_role != GlobalRole.ADMIN:
        member_project_ids = db.query(ProjectMember.project_id).filter(ProjectMember.user_id == current_user.id).subquery()
        task_query = task_query.filter(Task.project_id.in_(member_project_ids))

    total_tasks = task_query.count()
    todo_tasks = task_query.filter(Task.status == TaskStatus.TODO).count()
    in_progress_tasks = task_query.filter(Task.status == TaskStatus.IN_PROGRESS).count()
    done_tasks = task_query.filter(Task.status == TaskStatus.DONE).count()
    overdue_tasks = task_query.filter(Task.due_date < date.today(), Task.status != TaskStatus.DONE).count()

    my_open_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.assignee_id == current_user.id, Task.status != TaskStatus.DONE)
        .scalar()
    )

    return DashboardSummary(
        total_tasks=total_tasks,
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        done_tasks=done_tasks,
        overdue_tasks=overdue_tasks,
        my_open_tasks=my_open_tasks or 0,
    )

