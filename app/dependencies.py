from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import GlobalRole, Project, ProjectMember, ProjectRole, User
from app.security import decode_access_token


bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user


def require_global_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.global_role != GlobalRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


def get_project_membership(project_id: int, user_id: int, db: Session) -> ProjectMember | None:
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )


def can_view_project(project: Project, user: User, db: Session) -> bool:
    if user.global_role == GlobalRole.ADMIN or project.owner_id == user.id:
        return True
    membership = get_project_membership(project.id, user.id, db)
    return membership is not None


def can_manage_project(project: Project, user: User, db: Session) -> bool:
    if user.global_role == GlobalRole.ADMIN or project.owner_id == user.id:
        return True
    membership = get_project_membership(project.id, user.id, db)
    return membership is not None and membership.role == ProjectRole.ADMIN

