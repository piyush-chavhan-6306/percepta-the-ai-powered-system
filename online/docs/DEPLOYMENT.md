# PERCEPTA DEFENSE — COMPLETE ONLINE PRODUCTION DEPLOYMENT GUIDE

This document details the exact, reproducible steps for deploying the independent **PERCEPTA Online Cloud C2 System** across **Vercel** (Frontend), **Render** (FastAPI Backend), **Neon** (PostgreSQL Serverless), and **Supabase** (Authentication), adhering strictly to zero-cost, no-credit-card constraints.

---

## 1. System Architecture

```
                    INTERNET (HTTPS / WSS)
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
       VERCEL CLOUD                      RENDER CLOUD
     React / Vite SPA                   FastAPI Backend
    (percepta-c2.vercel.app)         (percepta.onrender.com)
             │                                 │
             │                        ┌────────┴────────┐
             ▼                        ▼                 ▼
       SUPABASE AUTH              NEON CLOUD       QUEUE WORKERS
      (JWT Identity)             (PostgreSQL)      (Async Ingestion)
             │                        │                 │
             └───────────► C2 ◄───────┴─────────────────┘
                           │
                    OBJECT STORAGE
                 (Uploads / Evidence)
```

---

## 2. Prerequisites & Free Tier Services

| Service | Role | Free Tier Specifications |
| :--- | :--- | :--- |
| **Vercel** | React + Vite Frontend Hosting | 100 GB Bandwidth, Global CDN Edge, Automatic SSL |
| **Render** | FastAPI Backend & WebSockets | 750 free instance hours/month, automatic HTTPS |
| **Neon** | PostgreSQL Database | 0.5 GB Serverless storage, connection pooling |
| **Supabase** | Operator Authentication & JWT | 50,000 MAU, Auth endpoints, Row-Level Security |

---

## 3. Deployment Sequence

### Step 1: Neon Cloud PostgreSQL Setup
1. Create a free project at [neon.tech](https://neon.tech).
2. Create database named `percepta_cloud`.
3. Copy the async connection string:
   ```env
   DATABASE_URL=postgresql+asyncpg://<USER>:<PASSWORD>@<ENDPOINT>.neon.tech/percepta_cloud?ssl=require
   ```
4. Run database migrations:
   ```bash
   cd online
   python -m database.run_migrations
   ```

### Step 2: Supabase Authentication Setup
1. Create a free project at [supabase.com](https://supabase.com).
2. In **Project Settings -> API**, obtain:
   - `Project URL`
   - `anon public` key
   - `service_role` secret key (Backend only — NEVER expose to frontend!)
3. In **Authentication -> URL Configuration**, add your Vercel domain to **Redirect URLs**:
   ```
   https://percepta-c2.vercel.app/**
   http://localhost:5000/**
   ```

### Step 3: Render Backend Deployment
1. Connect your GitHub repository to [render.com](https://render.com).
2. Select **New Web Service** and point to the repository:
   - **Root Directory**: `online`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r backend/requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2`
3. Configure Environment Variables in Render Dashboard:
   ```env
   ENVIRONMENT=production
   DATABASE_URL=postgresql+asyncpg://<USER>:<PASSWORD>@<ENDPOINT>.neon.tech/percepta_cloud?ssl=require
   SUPABASE_URL=https://<YOUR_PROJECT>.supabase.co
   SUPABASE_ANON_KEY=<ANON_KEY>
   SUPABASE_SERVICE_ROLE_KEY=<SERVICE_ROLE_KEY>
   CORS_ORIGINS=https://percepta-c2.vercel.app
   RAW_VIDEO_RETENTION_HOURS=24
   RETENTION_CHECK_INTERVAL_SECONDS=3600
   DEMO_MODE=false
   ```
4. Verify backend health endpoint:
   ```bash
   curl -I https://percepta-backend.onrender.com/health
   # Expected response: HTTP/1.1 200 OK
   ```

### Step 4: Vercel Frontend Deployment
1. Import your GitHub repository into [vercel.com](https://vercel.com).
2. Set configuration:
   - **Root Directory**: `online/frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Configure Environment Variables in Vercel:
   ```env
   VITE_API_URL=https://percepta-backend.onrender.com
   VITE_WS_URL=wss://percepta-backend.onrender.com/ws/events
   VITE_SUPABASE_URL=https://<YOUR_PROJECT>.supabase.co
   VITE_SUPABASE_ANON_KEY=<ANON_KEY>
   ```
4. Deploy. Vercel provisions global SSL and maps routes via `vercel.json`.

---

## 4. Operational Health & Readiness Endpoints

- **Liveness probe**: `GET /health` -> `{"status": "healthy", "service": "percepta_online"}`
- **Readiness probe**: `GET /ready` -> Checks database connectivity and worker queues.
- **Diagnostics**: `GET /api/database/diagnostics` -> Confirms table migrations and connection pooling.
