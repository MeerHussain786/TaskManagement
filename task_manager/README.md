# Enterprise Task Management System

A complete, production-ready Task Management system featuring a Next.js 15 frontend and a FastAPI backend using Clean Architecture.

This repository is organized into a monorepo structure:
- `/frontend` - Next.js React application
- `/backend` - FastAPI Python REST API

---

## Prerequisites

- **Node.js**: v18+ (for frontend)
- **Python**: v3.13+ (for backend)
- **Database**: SQLite (default for local dev) or PostgreSQL
- **Cache**: Redis 7+

---

## 1. Backend Setup (`/backend`)

The backend is built with FastAPI, SQLAlchemy 2.0 (async), and Alembic for migrations.

### Environment Setup
Navigate to the backend directory and create a virtual environment:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables (.env)
Create a `.env` file inside the `backend/` directory:
```env
# Example backend/.env
DATABASE_URL=sqlite+aiosqlite:///task_manager.db
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Migrations
Generate the initial database tables:
```bash
alembic upgrade head
```

### Run Backend
```bash
uvicorn main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 2. Frontend Setup (`/frontend`)

The frontend is an enterprise-grade UI using Next.js 15, Tailwind CSS v4, shadcn/ui, and Zustand.

### Installation
Navigate to the frontend directory:
```bash
cd frontend
npm install
```

### Environment Variables (.env)
Create a `.env` file inside the `frontend/` directory (if you have frontend-specific keys):
```env
# Example frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Frontend
Start the development server:
```bash
npm run dev
```
*(Note: If you use `npm run dev` from the frontend folder, it is configured to concurrently run both the frontend and backend servers automatically for convenience!)*

- Application: [http://localhost:3000](http://localhost:3000)

---

## Generating API Client

If the backend OpenAPI schema (`openapi.json`) changes, regenerate the React Query hooks from the frontend folder:
```bash
cd frontend
npx orval
```

## Docker Deployment

To run both services using Docker Compose:
```bash
docker-compose up -d --build
```
