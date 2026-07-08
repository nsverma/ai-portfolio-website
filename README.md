# AI / Machine Learning Portfolio Website

A full-stack, recruiter-facing portfolio showcasing Machine Learning, Deep Learning,
AI Agent, and Automation projects — with real authentication and an admin dashboard
to manage projects without touching code.

**Stack:** FastAPI + SQLAlchemy + JWT auth (backend) · React + Vite + Tailwind CSS + Framer Motion (frontend) · SQLite for local dev, Postgres-ready.

---

## Project Structure

```
ai-portfolio-website/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy models (User, Category, Project, ContactMessage)
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── routes/       # auth, projects, categories, contact routers
│   │   ├── auth/         # password hashing + JWT
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py       # FastAPI app instance
│   ├── main.py           # `uvicorn main:app` entry point
│   ├── requirements.txt
│   └── .env.example
├── database/
│   └── seed_data.py       # populates categories + ~34 sample projects + demo admin
├── frontend/
│   ├── src/
│   │   ├── components/    # Navbar, ProjectCard, LoginForm, DashboardLayout, etc.
│   │   ├── pages/         # Home, MachineLearning, DeepLearning, AIAgent, Automation, Dashboard, etc.
│   │   ├── services/      # axios API client
│   │   ├── context/       # AuthContext (JWT session handling)
│   │   ├── data/          # ML/DL/Agent/Automation submenu lists
│   │   └── styles/        # Tailwind + glassmorphism theme
│   ├── package.json
│   └── .env.example
└── README.md
```

---

## Running Locally

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # defaults to SQLite, no changes needed for local dev

uvicorn main:app --reload       # http://localhost:8000
```

Interactive API docs: http://localhost:8000/docs

### 2. Seed the database

Run once, after the backend has created `portfolio.db` (the first `uvicorn` run does this automatically):

```bash
cd backend
python ../database/seed_data.py
```

This creates the 4 categories, ~34 sample projects (covering every ML/DL/Agent/Automation
submenu so no page looks empty), and a demo admin login:

```
email:    admin@portfolio.dev
password: Admin@123
```

Replace the sample projects with your own via the dashboard once logged in, or edit
`database/seed_data.py` directly and re-run it.

### 3. Frontend (React + Vite)

```bash
cd frontend
npm install
cp .env.example .env             # VITE_API_URL=http://localhost:8000
npm run dev                      # http://localhost:5173
```

Open http://localhost:5173 — the first person to register at `/register` becomes the
site admin automatically (or just log in with the seeded demo admin above).

---

## Connecting PostgreSQL (Production)

The backend already uses SQLAlchemy, so switching databases is a one-line config change:

1. Create a Postgres database (locally, or via a host like Neon/Supabase/Railway/RDS).
2. In `backend/.env`, set:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```
3. Install the Postgres driver: `pip install psycopg2-binary` (left commented out in `requirements.txt` since it needs to compile against local Postgres headers and isn't needed for SQLite dev — if it fails to build on your machine, install Postgres itself first or use `psycopg2-binary` via your OS package manager).
4. Restart the backend — `Base.metadata.create_all()` will create the tables on Postgres
   the same way it did on SQLite.
5. Re-run `database/seed_data.py` against the new database if you want the sample data there too.

For a production app you outgrow `create_all()` with, add [Alembic](https://alembic.sqlalchemy.org/)
for versioned migrations — not required to get started, but worth adding once the schema
is stabilizing.

---

## Deployment Suggestions

| Layer | Recommended | Why |
|---|---|---|
| Backend (FastAPI) | Render, Railway, or Fly.io | Free/cheap tiers, simple `uvicorn` deploy, easy env var config |
| Frontend (React) | Vercel or Netlify | Zero-config static/SPA hosting, free tier, instant preview URLs for your resume link |
| Database | Neon, Supabase, or Railway Postgres | Free-tier managed Postgres — swap in via `DATABASE_URL` as described above |

Steps for a typical deploy:
1. Push this repo to GitHub.
2. Deploy `backend/` to Render/Railway as a Python web service (`uvicorn main:app --host 0.0.0.0 --port $PORT`), set `DATABASE_URL` and `SECRET_KEY` as environment variables there.
3. Deploy `frontend/` to Vercel/Netlify, set `VITE_API_URL` to your deployed backend URL.
4. Update `CORS_ORIGINS` in `backend/app/config.py` to include your deployed frontend URL.
5. Run `database/seed_data.py` once against the production database (or add your real projects directly via the dashboard).

---

## Security Notes
- Passwords are hashed with bcrypt (`passlib`), never stored in plain text.
- Auth uses stateless JWTs (`python-jose`) sent as `Authorization: Bearer <token>`.
- Only users with `role="admin"` can create/update/delete projects or view contact messages — the first registered user becomes admin automatically.
- Change `SECRET_KEY` in `.env` before deploying anywhere public.

## Customizing for Your Real Projects
1. Log in to `/dashboard` (seeded admin or your own registered account).
2. Use **Add New Project** to replace the sample data with your real ML/DL/Agent/Automation work.
3. Update `frontend/src/pages/About.jsx` and `Contact.jsx` with your real bio, links, and resume (`frontend/public/resume.pdf`).
4. Update GitHub/LinkedIn links in `Navbar.jsx`'s and `Footer.jsx`'s hardcoded hrefs, and in `HeroSection.jsx`.
