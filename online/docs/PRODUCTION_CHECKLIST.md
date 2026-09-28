# PERCEPTA ONLINE — PRODUCTION DEPLOYMENT & SMOKE TEST CHECKLIST

Use this checklist before and after deploying to Vercel and Render.

---

## Pre-Deployment Verification

- [x] **Zero Hardcoded Secrets**: Ensure `.env` is never committed; verify `.env.example` has generic placeholders.
- [x] **Frontend Production Build**: `npm run build` exits 0 with no TypeScript warnings or missing imports.
- [x] **Backend Clean Install**: `pip install -r backend/requirements.txt` succeeds without conflicting dependencies.
- [x] **Independent Execution**: `/online` runs cleanly without requiring parent project files or runtime dependencies.
- [x] **CORS Configuration**: Restrict allowed origins to deployed Vercel domain and localhost development ports.
- [x] **Database Migrations**: Run all database table schemas and verify indexes for `camera_id`, `incident_id`, and `created_at`.
- [x] **Storage Directory Permissions**: Verify write access to `storage/recordings`, `storage/uploads`, and `storage/evidence`.

---

## Production Smoke Test Verification

| Test Step | Component | Verification Criteria | Status |
| :--- | :--- | :--- | :--- |
| **1. Public Landing** | Vercel Frontend | Landing hero loads with 3D terrain canvas, zero console errors | PASS |
| **2. Authentication** | Supabase Auth | Sign in and session persistence work; unauthorized routes redirect | PASS |
| **3. C2 Dashboard** | Frontend SPA | Live telemetry loads; camera selector displays all registered feeds | PASS |
| **4. Multi-Camera Grid** | Layout Engine | 1×1, 2×2, and 3×3 layouts switch smoothly without crashing | PASS |
| **5. Independent Analysis** | Camera Manager | Stopping analysis on Cam 2 pauses Cam 2 while Cam 1 continues running | PASS |
| **6. Tripwire Plotting** | Interactive Canvas | Plotted dots land at cursor location; saved tripwire aligns with video | PASS |
| **7. Tripwire Crossing** | Incident Engine | Crossing triggers alert; parallel movement does NOT trigger false alarms | PASS |
| **8. Ghost Zone Intrusion** | Zone Monitor | Unconfigured camera produces ZERO fake perimeter alerts | PASS |
| **9. Paused Camera Freeze** | Snapshot API | Paused camera shows frozen frame and standby banner (no black screen) | PASS |
| **10. Mobile Responsiveness**| Responsive Layout | Dashboard scales smoothly to tablet and phone widths | PASS |
| **11. Chunked Upload** | Storage API | Large video uploads in binary chunks without loading into RAM | PASS |
| **12. 24h Raw Retention** | Retention Manager | Raw video purged after 24h; permanent forensic evidence retained | PASS |
| **13. AI Border Copilot** | Intelligence Engine| Responds accurately based on real system incident data | PASS |
| **14. Multi-Modal Sensing** | Sensor Pipeline | Optical RGB, IR Night Vision, and Thermal modalities render correctly | PASS |
