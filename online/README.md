# PERCEPTA DEFENSE — Autonomous Cloud-Hybrid Surveillance C2 Platform

PERCEPTA Online is an independent, production-grade Surveillance Command & Control (C2) web platform designed for border security forces. It delivers real-time AI perception, multi-camera matrix monitoring (1×1, 2×2, 3×3), sub-pixel zone and directional tripwire plotting, optical sensor diagnostics, tamper-evident forensic evidence chains, and a grounded AI Border Copilot.

---

## 1. System Architecture & Production Cloud Topology

```
                              INTERNET (HTTPS / WSS)
                                         │
             ┌───────────────────────────┴───────────────────────────┐
             ▼                                                       ▼
       VERCEL CLOUD                                            RENDER CLOUD
    React / Vite SPA                                         FastAPI Backend
 (Responsive Desktop / Tablet / Mobile)                    (Async REST & WebSockets)
             │                                                       │
             │                                    ┌──────────────────┴──────────────────┐
             ▼                                    ▼                                     ▼
       SUPABASE AUTH                         NEON CLOUD                           QUEUE WORKERS
 (JWT Operator Clearance)               (PostgreSQL Serverless)               (Chunked Ingestion)
             │                                    │                                     │
             └──────────────────► C2 ◄────────────┴─────────────────────────────────────┘
                                  │
                           OBJECT STORAGE
                      ┌───────────┴───────────┐
                      ▼                       ▼
               RAW SURVEILLANCE       FORENSIC EVIDENCE
             (24-Hour Auto-Purge)   (Permanent Retention)
```

---

## 2. Key Capabilities & Fixes

1. **Sub-Pixel Tripwire & Zone Plotting**:
   - Zero coordinate drift: Clicks are converted dynamically from live screen coordinates into frame coordinates.
   - Dual coordinate format compatibility: Seamlessly renders both normalized (`[0.0, 1.0]`) and pixel coordinates (`[0, 1280]`) on any viewport or device size.
2. **Strict Physical Crossing Validation**:
   - Boundary checks enforce matching coordinate systems (normalized vs pixel), rejecting mismatched cross-checks.
   - Physical movement thresholding: Rejects teleportation jumps ($> 250\text{px}$) and requires persistent tracks ($\ge 2$ frames).
   - Zero phantom alarms: Cameras without operator-plotted zones produce zero unsolicited perimeter intrusions.
3. **Independent Multi-Camera Analysis**:
   - In 1×1, 2×2, and 3×3 grid layouts, each camera tile features its own independent **START ANALYSIS** / **STOP ANALYSIS** toggle.
   - Pausing Cam 2 freezes Cam 2 on a clean standby snapshot with live telemetry while Cam 1 continues processing live frames without interruption.
4. **Fast Chunked / Resumable Video Ingestion**:
   - Streams 1 GB – 2 GB surveillance video in discrete binary chunks directly to storage handles without consuming server heap RAM.
   - Resumable upload session recovery, SHA-256 integrity verification, and instant upload cancellation.
5. **24-Hour Raw Video Retention with Permanent Forensic Evidence**:
   - Raw surveillance footage is automatically purged after 24 hours (`RAW_VIDEO_RETENTION_HOURS=24`).
   - Forensic snapshots, violation video clips, incident dossiers, and SHA-256 hashes are preserved permanently under chain-of-custody.
6. **Fully Responsive Across Desktop, Tablet, and Mobile**:
   - Responsive flex layouts, collapsible header telemetry, and touch-friendly controls.

---

## 3. Directory Layout

```
online/
├── frontend/             # React 19 + TypeScript + Vite + Tailwind C2 Web Application
│   ├── src/              # Components, Hooks, Pages, and Perception Visualizers
│   └── vercel.json       # Vercel Production Routing and Asset Caching Rules
├── backend/              # FastAPI Application (API, Ingestion, Perception, Gateway)
│   ├── api/              # REST Endpoints (Cameras, Incidents, Zones, Upload, Streaming)
│   ├── tracking/         # ByteTrack & Live Perception Worker Registry
│   ├── zones/            # Security Zones, Virtual Boundaries & PathGuard Corridors
│   └── requirements.txt  # Python Production Dependencies
├── copilot/              # 12 Grounded System Tools for AI Assistant
├── database/             # Neon PostgreSQL / SQLAlchemy Models and Migrations
├── auth/                 # Supabase Authentication & Multi-Tenant Clearance
├── sync/                 # Idempotent Edge-to-Cloud Synchronization Receiver
├── storage/              # Evidence Storage & 24h Raw Video Retention Manager
├── services/             # Asynchronous Queue Manager (PENDING -> PROCESSING -> COMPLETED)
├── docs/                 # Production Deployment & Setup Guides
│   ├── DEPLOYMENT.md     # Step-by-step Vercel, Render, Neon, Supabase deployment
│   ├── VIDEO_STORAGE.md  # Video ingestion & 24h retention policy documentation
│   ├── PRODUCTION_CHECKLIST.md  # Complete smoke test & verification checklist
│   └── OFFLINE_AND_ONLINE_RUN_GUIDE.md # Running offline edge & online C2
├── render.yaml           # Render Cloud Infrastructure Blueprint
├── vercel.json           # Vercel Cloud Root Configuration
├── .env.example          # Template Environment Variables with Safe Placeholders
└── README.md             # Project Overview and Documentation Index
```

---

## 4. Local Execution

### Backend
```bash
cd online
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend
```bash
cd online/frontend
npm install
npm run dev
```
Open `http://localhost:5000` to enter the C2 command center.

---

## 5. Production Cloud Deployment

Follow the dedicated guides:
- [Production Deployment Guide](docs/DEPLOYMENT.md)
- [Video Ingestion & Retention Architecture](docs/VIDEO_STORAGE.md)
- [Offline vs Online Operational Run Guide](docs/OFFLINE_AND_ONLINE_RUN_GUIDE.md)
- [Production Smoke Test Checklist](docs/PRODUCTION_CHECKLIST.md)
