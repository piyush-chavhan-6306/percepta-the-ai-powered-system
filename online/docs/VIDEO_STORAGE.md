# PERCEPTA DEFENSE — VIDEO INGESTION & 24-HOUR RETENTION ARCHITECTURE

Surveillance video data requires high-throughput ingestion, resilience across network interruptions, and strict adherence to evidence preservation policies. This document details the storage architecture for PERCEPTA Online.

---

## 1. High-Speed Chunked & Resumable Ingestion

For video recordings exceeding 1 GB – 2 GB, PERCEPTA avoids loading complete video streams into server RAM.

```
OPERATOR BROWSER / EDGE
           │
           │  1. POST /api/upload/init (filename, size, total_chunks)
           ▼
    FASTAPI BACKEND
           │
           │  2. Issue upload session [upl_xxxxxxxxxxxx]
           ▼
  CHUNKED DIRECT STREAM
           │
           │  3. POST /api/upload/chunk (upload_id, chunk_index, binary chunk)
           │     -> Written directly to disk buffer / storage
           │
           ▼
  COMPLETION & VERIFICATION
           │
           │  4. POST /api/upload/complete (upload_id)
           │     -> Assembles chunks, computes SHA-256 integrity hash
           │
           ▼
    ONLINE QUEUE
           │
           │  5. Dispatches JobType.VIDEO_UPLOAD to worker
           ▼
 PERCEPTION PIPELINE
```

### Key Capabilities
- **Direct Streaming**: Chunk payloads write straight to file handles without buffering in heap memory.
- **Resumability**: If a network failure occurs on chunk 45 of 100, the client queries `GET /api/upload/{upload_id}/status` and resumes from chunk 45, avoiding restarting from 0%.
- **Cancellation**: `DELETE /api/upload/{upload_id}` immediately cleans up temporary chunk files.
- **Concurrency**: Client-side concurrency throttled to 3–5 parallel requests.

---

## 2. The 24-Hour Video Retention Policy

SURVEILLANCE STORAGE LIFECYCLE:
- **Default Duration**: `RAW_VIDEO_RETENTION_HOURS=24` (Configurable in `.env`).
- **Target**: Applies ONLY to eligible raw surveillance recordings.

### Explicit Retention Segregation:

| Data Type | Storage Location | Retention Window | Purge Behavior |
| :--- | :--- | :--- | :--- |
| **Raw Surveillance Video** | `storage/recordings/`, `storage/uploads/` | **24 Hours** | Automatic background purge (marked `DELETED_AFTER_RETENTION`) |
| **Forensic Incident Snapshot** | `storage/snapshots/` | **Permanent** | NEVER deleted |
| **Forensic Violation Clip** | `storage/evidence/` | **Permanent / Legal Hold** | Retained according to chain-of-custody policy |
| **Incident Metadata & Threat Scores** | Neon PostgreSQL | **Permanent** | Retained with SHA-256 tamper-evident checksums |
| **Audit Logs & Alerts** | Neon PostgreSQL | **Permanent** | Retained indefinitely |

---

## 3. Evidence Hold Exception (Zero Evidence Loss)

If a raw surveillance video contains an incident under investigation:
1. The operator or incident engine marks the video with a **Forensic Evidence Hold**:
   ```python
   retention_manager.protect_video(video_identifier)
   ```
2. During the periodic cleanup cycle (`purge_expired_recordings`), any file under evidence hold is skipped:
   ```python
   if file_stem in self._protected_ids:
       logger.debug("Skipping: Protected by forensic evidence hold")
       continue
   ```
3. The raw footage remains intact until the incident is formally closed and cleared by an authorized operator.

---

## 4. Background Purge Worker

The background worker executes on a configurable schedule (default every 3600 seconds):
1. Computes the cutoff: `cutoff = now() - timedelta(hours=RAW_VIDEO_RETENTION_HOURS)`.
2. Inspects modification timestamps on raw video files.
3. Excludes protected files and evidence folders.
4. Unlinks expired files and logs freed bytes to structured telemetry.
5. In tests, `RAW_VIDEO_RETENTION_HOURS=1` or dry-run mode can be utilized.
