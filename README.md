# Team Task Manager (Python Full-Stack)

Team Task Manager is a full-stack web app built with FastAPI + SQLAlchemy + vanilla JS frontend.

## Features

- Authentication: signup, login, JWT auth
- Role-based access control:
  - Global roles: `admin`, `member`
  - Project roles: `admin`, `member`
- Project management:
  - Admin can create projects
  - Project admins can add/update project members
- Task management:
  - Create tasks, assign members, update status
  - Track overdue tasks
- Dashboard summary:
  - Total, todo, in-progress, done, overdue, my open tasks

## Tech Stack

- Backend: FastAPI
- Database: SQLAlchemy (SQLite by default, PostgreSQL via `DATABASE_URL`)
- Frontend: HTML/CSS/JavaScript served by FastAPI
- Auth: JWT (`python-jose`) + password hashing (`passlib`)

## Local Setup

1. Create virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy environment file and update values if needed:

   ```bash
   copy .env.example .env
   ```

3. Run the app:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Open:
   - App UI: `http://127.0.0.1:8000/`
   - API docs: `http://127.0.0.1:8000/docs`

## Core API Endpoints

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/projects`
- `GET /api/projects`
- `POST /api/projects/{project_id}/members`
- `GET /api/projects/{project_id}/members`
- `POST /api/projects/{project_id}/tasks`
- `GET /api/projects/{project_id}/tasks`
- `PATCH /api/tasks/{task_id}`
- `GET /api/tasks/my`
- `GET /api/tasks/overdue`
- `GET /api/dashboard/summary`

## Railway Deployment (Mandatory Requirement)

1. Push this project to GitHub.
2. Create a new project in Railway and connect your repo.
3. Add environment variables in Railway:
   - `DATABASE_URL` (Railway Postgres connection URL recommended)
   - `SECRET_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=120`
4. Railway will detect `railway.json` and run:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
   ```

5. Open your Railway public URL and verify:
   - Signup/Login works
   - Create project and add members
   - Create/assign/update tasks
   - Dashboard metrics update

