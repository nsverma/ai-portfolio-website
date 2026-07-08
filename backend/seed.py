"""Populate an empty database with the portfolio content.

Run from backend/ after creating the venv:
    ./venv/bin/python seed.py

Idempotent: skips any table that already has rows. Does not create users —
register your admin account through the API/UI instead.
"""

import json
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models.category import Category
from app.models.project import Project

SEED_FILE = Path(__file__).parent / "seed_data.json"


def main():
    Base.metadata.create_all(bind=engine)
    data = json.loads(SEED_FILE.read_text())
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            for row in data["categories"]:
                db.add(Category(**row))
            print(f"seeded {len(data['categories'])} categories")
        else:
            print("categories already present, skipping")
        if db.query(Project).count() == 0:
            for row in data["projects"]:
                db.add(Project(**row))
            print(f"seeded {len(data['projects'])} projects")
        else:
            print("projects already present, skipping")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
