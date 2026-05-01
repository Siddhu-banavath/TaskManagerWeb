from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import GlobalRole, ProjectRole, TaskStatus


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    global_role: GlobalRole = GlobalRole.MEMBER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    global_role: GlobalRole

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectMemberUpsert(BaseModel):
    user_id: int
    role: ProjectRole = ProjectRole.MEMBER


class ProjectMemberOut(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: ProjectRole
    joined_at: datetime
    user: UserOut

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    assignee_id: int | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    assignee_id: int | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    project_id: int
    creator_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    done_tasks: int
    overdue_tasks: int
    my_open_tasks: int

