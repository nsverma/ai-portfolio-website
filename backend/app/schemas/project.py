from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.category import CategoryOut


class ProjectBase(BaseModel):
    title: str
    slug: str
    category_id: int
    method_or_algorithm: str
    short_description: str
    problem_statement: Optional[str] = None
    dataset_description: Optional[str] = None
    business_use_case: Optional[str] = None
    workflow_steps: Optional[str] = None
    tools_used: Optional[str] = None
    technologies_used: Optional[str] = None
    evaluation_metrics: Optional[str] = None
    results: Optional[str] = None
    key_learning: Optional[str] = None
    difficulty_level: str = "Beginner"
    status: str = "Completed"
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    dataset_url: Optional[str] = None
    image_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    category_id: Optional[int] = None
    method_or_algorithm: Optional[str] = None
    short_description: Optional[str] = None
    problem_statement: Optional[str] = None
    dataset_description: Optional[str] = None
    business_use_case: Optional[str] = None
    workflow_steps: Optional[str] = None
    tools_used: Optional[str] = None
    technologies_used: Optional[str] = None
    evaluation_metrics: Optional[str] = None
    results: Optional[str] = None
    key_learning: Optional[str] = None
    difficulty_level: Optional[str] = None
    status: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    dataset_url: Optional[str] = None
    image_url: Optional[str] = None


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryOut

    class Config:
        from_attributes = True
