from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, nullable=False, index=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    # e.g. "Linear Regression", "CNN", "RAG-based Agent", "Report Automation"
    method_or_algorithm = Column(String(120), nullable=False, index=True)

    short_description = Column(String(500), nullable=False)
    problem_statement = Column(Text, nullable=True)
    dataset_description = Column(Text, nullable=True)
    business_use_case = Column(Text, nullable=True)
    workflow_steps = Column(Text, nullable=True)  # newline separated steps
    tools_used = Column(String(500), nullable=True)  # comma separated
    technologies_used = Column(String(500), nullable=True)  # comma separated
    evaluation_metrics = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    key_learning = Column(Text, nullable=True)

    difficulty_level = Column(String(20), nullable=False, default="Beginner")
    status = Column(String(20), nullable=False, default="Completed")

    github_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    dataset_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="projects")
