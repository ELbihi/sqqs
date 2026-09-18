from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Project, User
from pydantic import BaseModel

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectIn(BaseModel):
    name: str = "Untitled project"


class ProjectOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[ProjectOut])
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.owner_id == user.id).all()


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    body: ProjectIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    project = Project(owner_id=user.id, name=body.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    obj = db.get(Project, project_id)
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    db.delete(obj)
    db.commit()
