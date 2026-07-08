from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.category import Category
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _base_query(db: Session):
    return db.query(Project).options(joinedload(Project.category))


@router.get("", response_model=list[ProjectOut])
def list_projects(
    category: str | None = None,
    method: str | None = None,
    status: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = _base_query(db)

    if category:
        query = query.join(Category).filter(Category.slug == category)
    if method:
        query = query.filter(Project.method_or_algorithm == method)
    if status:
        query = query.filter(Project.status == status)
    if difficulty:
        query = query.filter(Project.difficulty_level == difficulty)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Project.title.ilike(like),
                Project.short_description.ilike(like),
                Project.method_or_algorithm.ilike(like),
            )
        )

    return query.order_by(Project.created_at.desc()).all()


@router.get("/category/{category_slug}", response_model=list[ProjectOut])
def get_projects_by_category(category_slug: str, db: Session = Depends(get_db)):
    return (
        _base_query(db)
        .join(Category)
        .filter(Category.slug == category_slug)
        .order_by(Project.created_at.desc())
        .all()
    )


@router.get("/method/{method}", response_model=list[ProjectOut])
def get_projects_by_method(method: str, db: Session = Depends(get_db)):
    return (
        _base_query(db)
        .filter(Project.method_or_algorithm == method)
        .order_by(Project.created_at.desc())
        .all()
    )


@router.get("/{id_or_slug}", response_model=ProjectOut)
def get_project(id_or_slug: str, db: Session = Depends(get_db)):
    query = _base_query(db)
    project = None
    if id_or_slug.isdigit():
        project = query.filter(Project.id == int(id_or_slug)).first()
    if project is None:
        project = query.filter(Project.slug == id_or_slug).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    if db.query(Project).filter(Project.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Project slug already exists")
    if not db.query(Category).filter(Category.id == payload.category_id).first():
        raise HTTPException(status_code=400, detail="Category does not exist")

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return None
