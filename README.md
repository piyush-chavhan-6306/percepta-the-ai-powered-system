# PERCEPTA DEFENCE — Cloud-Hybrid Online C2 Platform

> **AI Intelligence Layer for Border Surveillance & Autonomous Tactical C2 (Smart India Hackathon Prototype)**

PERCEPTA Defence is a tactical surveillance command-and-control (C2) platform engineered for forward border outposts, corridor monitoring, and strategic perimeter security. It combines edge-first, multi-modal perception with a resilient cloud command-and-control layer.

---

## 1. What It Is

PERCEPTA transforms conventional CCTV and electro-optical/infrared (EO/IR) surveillance feeds into proactive tactical intelligence:
- **Autonomous Threat Detection:** Continuous object detection and multi-object tracking (person, vehicle, convoy, aerial drone surrogates).
- **Tactical Rule Engine:** Real-time evaluation of restricted polygon security zones and directional tripwires.
- **Unified Threat Scoring:** Single source of truth for threat severity (`CRITICAL`, `RESTRICTED`, `NORMAL`), cleanly separated from incident types.
- **PathGuard Route Integrity:** Active patrol corridor monitoring and lateral excursion violation alerts.
- **Predicted Blind Spot Analysis:** Sensor telemetry and optical quality gap estimation without fabricating false geospatial coordinates.
- **Camera Trust Diagnostics:** Real-time optical lens quality, glare, occlusion, and stream freeze scoring.
- **Triple-A Forensic Evidence:** Auto-capture of cropped target, scene snapshot, and tamper-proof SHA-256 cryptographic integrity hashes.
- **Grounded AI Defence Copilot:** Natural-language assistant strictly backed by 12 structured system tools without model hallucinations.

---

## 2. Cloud-Hybrid Architecture

```
                    PERCEPTA ONLINE
                           │
            ┌──────────────┴──────────────┐
            │                             │
          EDGE                          CLOUD
            │                             │
       Camera Input                  User / Supabase Auth
            │                        Neon PostgreSQL
       YOLOv8 Detection              Metadata & Incidents
            │                        Evidence Records
       ByteTrack                     Sync Receiver
            │                        Online C2 Web App
       Zones & Tripwires             Grounded Copilot
       Incidents & Alerts            Chunked Upload API
            │
       Local Buffer
            │
            └───────────────► CLOUD (Reconciled Sync)
```

- **Edge Layer:** Heavy vision inference (YOLOv8/ONNX, ByteTrack, zone evaluation, optical diagnostics) runs locally on surveillance nodes. Heavy inference is NOT dumped into serverless functions.
- **Cloud Layer:** Multi-tenant user isolation, Supabase authentication, Neon PostgreSQL metadata persistence, forensic evidence verification, real-time WebSocket feeds, and Copilot intelligence.
- **Offline System (Reference Only):** PERCEPTA also provides a standalone air-gapped desktop application in `/offline`. *Note: The offline system is decoupled and handled separately; this implementation focuses strictly on `/online` and shared contracts in `/shared`.*

---

## 3. Technology Stack

### Frontend (`online/frontend`)
- **Framework:** React 19 + TypeScript + Vite
- **Styling:** Tailwind CSS + Tactical Glassmorphic Design System
- **Animation:** Motion (Framer Motion) + Lucide Icons
- **Auth SDK:** `@supabase/supabase-js`

### Backend (`online/backend`)
- **API Framework:** FastAPI (Python 3.11+) + Uvicorn
- **Concurrency & Async:** Asyncio, SlowAPI Rate Limiting
- **Database ORM:** SQLAlchemy 2.0 (Async) + `asyncpg` + `aiosqlite`
- **Vision & Tracking:** OpenCV, Ultralytics YOLOv8, ByteTrack, PyTorch
- **Queue Manager:** In-memory asynchronous worker pool with retry policies

### Database & Cloud Services (100% Free Tiers — No Credit Card Required)
- **Database:** Neon Serverless PostgreSQL (Free Tier: 0.5 GiB, branching)
- **Authentication:** Supabase Auth (Free Tier: 50,000 MAU)
- **Backend Hosting:** Render Web Service (Free Tier)
- **Frontend Hosting:** Vercel Hobby (Free Tier)

---

## 4. Local Development & Quick Start

### Prerequisites
- Python 3.10+ (Recommended: Python 3.11 or 3.12)
- Node.js 18+ and npm
- Git

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/percepta-defence-c2.git
cd "percepta-defence-c2"

# Copy template environment file
cp .env.example .env
```

Edit `.env` with your Supabase and Neon PostgreSQL keys (see [docs/ONLINE_DEPLOYMENT.md](docs/ONLINE_DEPLOYMENT.md)).

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# or: source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run the Online FastAPI Backend
uvicorn online.backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation is available at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd online/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Demo Camera & Sources

PERCEPTA Online avoids fabricating fake surveillance networks:
- **Default Demo Source:** `virat_cctv.mp4` (standardized VIRAT dataset sample) registered as **`CAM-01 [DEMO SOURCE]`**.
- **Standby Mode:** Cameras start in standby. Perception analysis begins only when the operator clicks **START ANALYSIS**.
- **Empty Grid Slots:** If fewer than 4 or 9 cameras exist, the 2×2 and 3×3 grids show clear standby slots rather than inventing mock feeds.
- **RTSP / IP Cameras:** Operators can add live RTSP feeds or upload recorded footage via the modal.

---

## 6. Testing

Run the full automated test suite covering all operational dimensions:
```bash
# Run all online and architectural tests
pytest tests/test_online_capabilities.py tests/test_online_offline_architecture.py tests/test_user_isolation_and_auth.py -v
```

### Verified Test Categories:
1. **Authentication & Session:** Supabase JWT parsing, session persistence, invalid token rejection.
2. **Multi-Tenant User Isolation:** User A and User B cannot view each other's cameras, incidents, evidence, or Copilot answers.
3. **Multi-Object Tracking:** Concurrent objects (A, B, C) receive distinct, collision-free tracking IDs.
4. **PathGuard Route Integrity:** Authorized corridor traversal passes; lateral excursions trigger deviation incidents.
5. **Predicted Blind Spot:** Coverage gaps and sensor occlusions evaluated with uncertainty levels.
6. **Camera Trust:** Lens occlusion, optical blur, and stream freezes flagged with quantitative diagnostic scores.
7. **Modality Indicators:** RGB (Blue/Cyan), IR (Green dashed), Thermal (Red dashed).
8. **Asynchronous Job Queue:** State lifecycle (`PENDING` $\to$ `PROCESSING` $\to$ `COMPLETED`).

---

## 7. Security & Tenant Isolation

- **Zero Passwords in Database:** Password authentication is delegated entirely to Supabase Auth.
- **Backend Authorization Enforcement:** Every camera, incident, alert, evidence record, and Copilot query enforces strict `user_id` filtering.
- **No Service Keys in Frontend:** Only `VITE_SUPABASE_ANON_KEY` is exposed in the web client. The `SUPABASE_SERVICE_ROLE_KEY` is strictly confined to the backend environment.
- **Tamper-Proof Evidence:** Incident crops and scene frames are hashed using SHA-256 upon generation.

---

## 8. Limitations & Honest Implementation Status

- **Cross-Camera Re-Identification:** Cross-camera global identity association across independent camera coordinates is reported as **`Not Yet Implemented`** rather than mocked with artificial matching.
- **Thermal Radiometric Temperature:** Unless calibrated thermal radiometric metadata is provided by the hardware stream, thermal temperature numbers are not fabricated. Modality is processed as an optical spectrum.
- **Geospatial Mapping:** Field-of-view blind spots are estimated from camera positioning and optical health. Accurate geographic polygon overlays require surveyor GIS calibration.

---

## 9. Cloud Deployment

For step-by-step instructions on deploying the frontend to **Vercel** and backend to **Render** with **Neon** and **Supabase**, consult:
👉 **[docs/ONLINE_DEPLOYMENT.md](docs/ONLINE_DEPLOYMENT.md)**
