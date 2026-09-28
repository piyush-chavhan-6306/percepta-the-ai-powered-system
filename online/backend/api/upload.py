"""
PERCEPTA ONLINE CHUNKED & RESUMABLE VIDEO UPLOAD API
Handles streaming chunked uploads (1GB, 1.5GB, 2GB+) without loading whole files into RAM,
providing progress tracking, resumption, and SHA-256 integrity verification.
"""
from datetime import datetime, timezone
import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends
from pydantic import BaseModel
try:
    from auth.supabase_auth import AuthenticatedUser, get_current_user
except ImportError:
    from online.auth.supabase_auth import AuthenticatedUser, get_current_user

try:
    from services.queue_manager import JobType, get_queue_manager
except ImportError:
    from online.services.queue_manager import JobType, get_queue_manager

logger = logging.getLogger("percepta.online.upload")
router = APIRouter(prefix="/api/upload", tags=["Video Upload"])

UPLOAD_TMP_DIR = Path("storage/upload_chunks")
UPLOAD_FINAL_DIR = Path("storage/uploads")


class InitUploadRequest(BaseModel):
    filename: str
    total_size_bytes: int
    total_chunks: int
    expected_sha256: Optional[str] = None
    camera_name: Optional[str] = None
    camera_type: str = "RGB"  # RGB, IR, THERMAL
    location_label: Optional[str] = None


class InitUploadResponse(BaseModel):
    upload_id: str
    chunk_size_bytes: int
    total_chunks: int
    status: str


class UploadStatusResponse(BaseModel):
    upload_id: str
    filename: str
    total_chunks: int
    uploaded_chunks: List[int]
    progress_percent: float
    status: str
    final_file_path: Optional[str] = None


# In-memory tracking of active upload sessions (backed by disk temporary chunk directory)
_upload_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/init", response_model=InitUploadResponse)
async def init_chunked_upload(
    req: InitUploadRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Initiates a resumable chunked upload session for large surveillance files."""
    upload_id = f"upl_{uuid.uuid4().hex[:12]}"
    session_dir = UPLOAD_TMP_DIR / upload_id
    session_dir.mkdir(parents=True, exist_ok=True)

    session = {
        "upload_id": upload_id,
        "filename": req.filename,
        "total_size": req.total_size_bytes,
        "total_chunks": req.total_chunks,
        "expected_sha256": req.expected_sha256,
        "camera_name": req.camera_name,
        "camera_type": req.camera_type,
        "location_label": req.location_label,
        "user_id": user.user_id,
        "uploaded_chunks": set(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "UPLOADING",
    }
    _upload_sessions[upload_id] = session
    logger.info(f"Initialized chunked upload [{upload_id}] for {req.filename} ({req.total_size_bytes} bytes, {req.total_chunks} chunks)")

    return InitUploadResponse(
        upload_id=upload_id,
        chunk_size_bytes=int(req.total_size_bytes / max(1, req.total_chunks)),
        total_chunks=req.total_chunks,
        status="INITIALIZED",
    )


@router.post("/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Receives and writes an individual binary chunk directly to disk buffer."""
    session = _upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session expired or invalid")

    session_dir = UPLOAD_TMP_DIR / upload_id
    chunk_file = session_dir / f"chunk_{chunk_index:05d}.part"

    content = await chunk.read()
    with open(chunk_file, "wb") as f:
        f.write(content)

    session["uploaded_chunks"].add(chunk_index)
    logger.debug(f"Received chunk {chunk_index} for [{upload_id}] ({len(content)} bytes)")

    progress = round((len(session["uploaded_chunks"]) / session["total_chunks"]) * 100.0, 1)
    return {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "uploaded_count": len(session["uploaded_chunks"]),
        "total_chunks": session["total_chunks"],
        "progress_percent": progress,
        "status": "CHUNK_SAVED",
    }


@router.post("/complete")
async def complete_chunked_upload(
    upload_id: str = Form(...),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Reassembles all received chunks into the final video file and computes SHA-256."""
    session = _upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session_dir = UPLOAD_TMP_DIR / upload_id
    if len(session["uploaded_chunks"]) < session["total_chunks"]:
        missing = set(range(session["total_chunks"])) - session["uploaded_chunks"]
        raise HTTPException(status_code=400, detail=f"Incomplete upload. Missing chunks: {list(missing)[:10]}")

    UPLOAD_FINAL_DIR.mkdir(parents=True, exist_ok=True)
    clean_name = "".join(c for c in session["filename"] if c.isalnum() or c in (".", "-", "_"))
    final_path = UPLOAD_FINAL_DIR / f"{upload_id}_{clean_name}"

    hasher = hashlib.sha256()
    total_written = 0

    with open(final_path, "wb") as out_f:
        for idx in range(session["total_chunks"]):
            part_path = session_dir / f"chunk_{idx:05d}.part"
            if not part_path.exists():
                raise HTTPException(status_code=500, detail=f"Corrupt chunk {idx} missing on disk")
            with open(part_path, "rb") as in_f:
                data = in_f.read()
                out_f.write(data)
                hasher.update(data)
                total_written += len(data)

    computed_sha256 = hasher.hexdigest()

    # Clean up chunk directory
    try:
        for p in session_dir.glob("*"):
            p.unlink()
        session_dir.rmdir()
    except Exception as ex:
        logger.warning(f"Failed to cleanup chunk dir: {ex}")

    session["status"] = "COMPLETED"
    session["final_path"] = str(final_path.as_posix())
    session["sha256"] = computed_sha256

    # Enqueue background processing job in OnlineQueueManager
    q_mgr = get_queue_manager()
    await q_mgr.enqueue(
        job_type=JobType.VIDEO_UPLOAD,
        payload={
            "upload_id": upload_id,
            "file_path": str(final_path),
            "size_bytes": total_written,
            "sha256": computed_sha256,
            "camera_name": session.get("camera_name"),
            "camera_type": session.get("camera_type"),
        },
        user_id=user.user_id,
    )

    logger.info(f"Successfully assembled video file [{final_path.name}] ({total_written} bytes, SHA-256: {computed_sha256[:12]}...)")

    return {
        "upload_id": upload_id,
        "filename": final_path.name,
        "file_path": str(final_path.as_posix()),
        "size_bytes": total_written,
        "sha256": computed_sha256,
        "status": "COMPLETED",
    }


@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
@router.get("/status/{upload_id}", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve chunk upload progress and status."""
    session = _upload_sessions.get(upload_id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    uploaded = sorted(list(session["uploaded_chunks"]))
    prog = round((len(uploaded) / session["total_chunks"]) * 100.0, 1) if session["total_chunks"] > 0 else 0.0

    return UploadStatusResponse(
        upload_id=upload_id,
        filename=session["filename"],
        total_chunks=session["total_chunks"],
        uploaded_chunks=uploaded,
        progress_percent=prog,
        status=session["status"],
        final_file_path=session.get("final_path"),
    )


@router.delete("/{upload_id}")
async def cancel_chunked_upload(
    upload_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Cancel an in-progress chunked upload and clean up disk buffer."""
    session = _upload_sessions.pop(upload_id, None)
    session_dir = UPLOAD_TMP_DIR / upload_id
    deleted_chunks = 0
    if session_dir.exists():
        for p in session_dir.glob("*"):
            p.unlink(missing_ok=True)
            deleted_chunks += 1
        session_dir.rmdir()

    logger.info(f"Cancelled upload [{upload_id}], purged {deleted_chunks} temporary chunks")
    return {
        "upload_id": upload_id,
        "status": "CANCELLED",
        "purged_chunks": deleted_chunks,
    }
