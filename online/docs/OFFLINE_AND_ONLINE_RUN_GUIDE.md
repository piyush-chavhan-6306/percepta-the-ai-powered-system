# PERCEPTA DEFENSE — COMPLETE OPERATIONAL RUN GUIDE
### Running the Offline Edge System and the Online Cloud C2 System

PERCEPTA operates in a dual-tier defense topology:
1. **Offline System (`/offline` & local edge)**: Dedicated high-speed YOLO + ByteTrack neural inference engine designed for physical border post workstations, operating with or without internet.
2. **Online System (`/online` & cloud)**: Remote Command & Control (C2) web platform deployed on Vercel, Render, Neon, and Supabase, enabling authorized command staff to monitor live streams, audit incidents, and investigate threats.

---

## 1. How to Run the Offline Edge System

### Prerequisites
- Python 3.10+ installed
- Local webcam, USB thermal/night vision sensor, or surveillance video files

### Quick Start
```bash
# 1. Navigate to project root
cd "d:\New Compressed (zipped) Folder\SIH   border cctv"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Launch Offline C2 Desktop Interface
python offline/desktop/main.py
```

### Building the Standalone Offline Executable (.EXE)
To generate the standalone zero-dependency executable for offline deployment:
```bash
python offline/desktop/build_exe.py
```
The compiled executable is written to `offline/dist/PERCEPTA_Defense_C2.exe`.

---

## 2. How to Run and Use the Online Cloud System

The `/online` project is 100% standalone and independent.

### Running Locally for Development / Testing

#### Start the Online Backend:
```bash
cd online
..\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend initializes REST endpoints, WebSockets at `/ws/events`, and the in-memory/Neon database.

#### Start the Online Frontend:
```bash
cd online/frontend
npm install
npm run dev
```
Open `http://localhost:5000` in your web browser.

### Using the Online C2 Interface
1. **Landing Portal**: Click **ENTER C2** to launch the surveillance console.
2. **Multi-Camera Grid**:
   - Switch between **1×1**, **2×2**, and **3×3** grid layouts.
   - Click any camera tile to open it in focused **Solo View**.
   - Use the individual **START ANALYSIS** / **STOP ANALYSIS** controls on each camera tile to pause or resume analysis per sensor independently.
3. **Zone & Tripwire Plotting**:
   - In 1×1 view, click **+ ZONE** or **+ TRIPWIRE**.
   - Click on the video feed to plot vertices with sub-pixel alignment.
   - Set severity (`RESTRICTED` / `CRITICAL`) and directional trigger (`BIDIRECTIONAL`, `NORTH`, `SOUTH`, `EAST`, `WEST`).
   - Click **SAVE**. The tripwire triggers alerts only when physical crossings occur.
4. **Sensor Diagnostics**:
   - Inspect optical clarity, lens tampering, and frame jitter in the real-time **Camera Trust HUD**.
   - Switch modalities seamlessly between **Optical RGB**, **IR Night Vision**, and **Thermal Radiometry**.
5. **AI Border Copilot**:
   - Use natural language to query incidents: *"What happened today?"*, *"Which camera detected restricted breaches?"*, *"Show thermal incidents."*

---

## 3. How Offline Edge and Online Cloud Synchronize

When edge cameras generate threat detections:
1. The **Edge Incident Engine** logs the incident, captures a forensic snapshot, and stores it in the local SQLite audit log.
2. If internet connectivity is available, the **Sync Manager** (`online/sync/sync_manager.py`) streams incidents, alerts, and snapshots to the **Online Cloud C2** via encrypted HTTPS.
3. If the border post loses internet, incidents are queued safely on disk. Upon reconnection, all backlogged records synchronize automatically without data loss or duplication.
