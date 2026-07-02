# Enterprise Task Management System 🚀

A complete, production-ready full-stack Task Management application featuring a beautifully designed Next.js frontend and a highly scalable FastAPI Python backend using Clean Architecture.

This repository is organized as a monorepo:
- `frontend/` - Next.js 15, React 19, Tailwind CSS v4, Zustand, and shadcn/ui.
- `backend/` - FastAPI, SQLAlchemy 2.0 (async), PostgreSQL/SQLite, and Redis.

---

## 🌟 Key Features

- **Modern UI/UX**: Premium aesthetic with micro-animations, glassmorphism, and responsive layouts.
- **Clean Architecture Backend**: Strict separation of concerns (Presentation, Application, Domain, and Infrastructure).
- **Asynchronous Stack**: Fully async database transactions via `FastAPI` and `SQLAlchemy 2.0`.
- **JWT Security & Refresh Token Rotation**: Safe session maintenance using secure JWT rotation.
- **Cache-Aside Pattern**: Low-latency backend endpoints powered by Redis caching.
- **Type-Safe API Contracts**: The frontend uses `orval` to auto-generate React Query hooks directly from the backend's OpenAPI schema.

---

## 🛠 Technology Stack

### Frontend
| Component | Technology |
| --- | --- |
| **Framework** | Next.js 15 (App Router), React 19 |
| **Styling** | Tailwind CSS v4, shadcn/ui, Radix UI |
| **State Management** | Zustand (Auth/Theme), TanStack Query v5 |
| **Forms** | React Hook Form, Zod |
| **API Client** | Orval (OpenAPI to TS generator), Axios |

### Backend
| Component | Technology |
| --- | --- |
| **Framework** | FastAPI (Python 3.13+) |
| **ORM** | SQLAlchemy 2.x (Async) |
| **Database** | PostgreSQL 16 (Prod) / SQLite (Dev) |
| **Cache & Security** | Redis 7, Bcrypt, Jose JWT |
| **Migrations** | Alembic |

---

## 💻 Local Development Setup

### 1. Backend Setup
Create your virtual environment and install dependencies:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Set up your environment and run database migrations:
```bash
cp .env.example .env
alembic upgrade head
```

### 2. Frontend Setup
In a new terminal window, install your frontend dependencies:
```bash
cd frontend
npm install
```

### 3. Run the Full Stack
You can start *both* the frontend and backend simultaneously using the frontend's built-in dev script!
```bash
cd frontend
npm run dev
```
- **Application UI:** [http://localhost:3000](http://localhost:3000)
- **Backend Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🚀 Production Deployment

This project is configured for easy deployment using **Vercel** for the frontend and **Render** for the backend.

### 1. Backend (Render)
This repository includes a `render.yaml` Blueprint. 
1. Log into Render and click **New > Blueprint**.
2. Connect this repository. Render will automatically detect the backend and host it as a web service.
3. Grab your hosted Render URL.

### 2. Frontend (Vercel)
1. Import this repository into Vercel.
2. In the setup screen, set the **Root Directory** to `frontend`.
3. Add an Environment Variable: 
   - `NEXT_PUBLIC_API_URL` = `<your-render-backend-url>`
4. Deploy!

---

## 📊 Observability & Testing

- **Testing suite**: The backend features over 95% test coverage tracking unit, integration, and End-to-End routes via `pytest`.
- **Structured JSON Logs**: Machine-parseable logs formatted with context details.
- **Metrics**: Exposed at `GET /metrics` for Prometheus scraping.