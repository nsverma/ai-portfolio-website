from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes import auth, categories, contact, demos, projects

# Dev convenience: creates tables if they don't exist yet.
# For production, prefer explicit migrations (see README).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI/ML Portfolio API",
    description="Backend for a recruiter-facing AI/ML/Automation portfolio site.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(projects.router)
app.include_router(contact.router)
app.include_router(demos.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI/ML Portfolio API is running"}
