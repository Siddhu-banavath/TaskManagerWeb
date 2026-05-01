from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import (
    can_manage_project,
    can_view_project,
    get_current_user,
    get_db,
    get_project_or_404,
    get_project_membership,
)
from app.models import GlobalRole, Project, ProjectMember, ProjectRole, User
from app.schemas import ProjectCreate, ProjectMemberOut, ProjectMemberUpsert, ProjectOut


router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.global_role != GlobalRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create projects.")

    project = Project(name=payload.name.strip(), description=payload.description, owner_id=current_user.id)
    db.add(project)
    db.flush()

    owner_membership = ProjectMember(project_id=project.id, user_id=current_user.id, role=ProjectRole.ADMIN)
    db.add(owner_membership)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.global_role == GlobalRole.ADMIN:
        return db.query(Project).order_by(Project.created_at.desc()).all()

    member_project_ids = db.query(ProjectMember.project_id).filter(ProjectMember.user_id == current_user.id).subquery()
    return (
        db.query(Project)
        .filter(Project.id.in_(member_project_ids))
        .order_by(Project.created_at.desc())
        .all()
    )


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project_or_404(project_id, db)
    if not can_view_project(project, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this project.")
    return project


@router.post("/{project_id}/members", response_model=ProjectMemberOut, status_code=status.HTTP_201_CREATED)
def add_or_update_member(
    project_id: int,
    payload: ProjectMemberUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    if not can_manage_project(project, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot manage members in this project.")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    membership = get_project_membership(project_id, payload.user_id, db)
    if membership:
        membership.role = payload.role
    else:
        membership = ProjectMember(project_id=project_id, user_id=payload.user_id, role=payload.role)
        db.add(membership)

    db.commit()
    db.refresh(membership)
    return membership


@router.get("/{project_id}/members", response_model=list[ProjectMemberOut])
def list_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project_or_404(project_id, db)
    if not can_view_project(project, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this project.")
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()

