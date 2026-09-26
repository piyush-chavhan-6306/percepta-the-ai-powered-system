"""
Border Intelligence Evidence Snapshot Extractor & Archival Module.
Persists visual JPEG snapshot frames, face crops, and license plate crops with bounding box evidence.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import cv2
import numpy as np
from pydantic import BaseModel, Field

from backend.config import get_settings


class SnapshotMetadata(BaseModel):
    snapshot_id: str
    incident_id: Union[str, UUID]
    camera_id: str
    frame_number: int
    trigger_reason: str
    file_path: str
    file_uri: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidencePackageMetadata(BaseModel):
    snapshot_id: str
    incident_id: Union[str, UUID]
    camera_id: str
    frame_number: int
    trigger_reason: str
    file_path: str
    file_uri: str
    face_snapshot_uri: Optional[str] = None
    anpr_snapshot_uri: Optional[str] = None
    sharpness_score: float = 0.0
    confidence: float = 0.0
    modality: str = "STANDARD"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BestEvidenceFrameSelector:
    """
    Evaluates candidate stream frames during an incident to identify the highest-quality
    forensic evidence frame based on target confidence, optical sharpness (Laplacian variance),
    and bounding box visibility.
    """

    @staticmethod
    def calculate_sharpness(image: np.ndarray) -> float:
        """Compute Laplacian variance representing image sharpness / focus."""
        if image is None or image.size == 0:
            return 0.0
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    @classmethod
    def score_frame_quality(
        cls,
        image: np.ndarray,
        confidence: float,
        bbox: Optional[List[float]] = None,
    ) -> float:
        """Composite quality metric (0.0 to 100.0)."""
        sharpness = cls.calculate_sharpness(image)
        # Normalize sharpness (50-500 typical range mapped to 0-1)
        sharp_norm = min(max(sharpness / 300.0, 0.0), 1.0)
        conf_norm = min(max(confidence, 0.0), 1.0)

        # Center/size weight
        size_norm = 0.5
        if bbox and len(bbox) >= 4 and image is not None:
            h, w = image.shape[:2]
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            box_area = (bw * bh) / max(w * h, 1)
            size_norm = min(box_area * 10.0, 1.0)

        composite = (0.45 * conf_norm + 0.35 * sharp_norm + 0.20 * size_norm) * 100.0
        return round(composite, 2)


class SnapshotArchiveManager:
    """Manages saving, indexing, and serving visual snapshot evidence for incident dossiers."""

    def __init__(self, snapshot_dir: Optional[str] = None) -> None:
        settings = get_settings()
        self.snapshot_dir = Path(snapshot_dir or os.path.join(settings.STORAGE_DIR, "snapshots"))
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(
        self,
        incident_id: Union[str, UUID],
        image: np.ndarray,
        camera_id: str = "CAM-01",
        frame_number: int = 0,
        trigger_reason: str = "RESTRICTED_ZONE_BREACH",
        bounding_boxes: Optional[List[List[float]]] = None,
        modality: str = "STANDARD",
    ) -> SnapshotMetadata:
        """Save a surveillance snapshot image with optional annotated target boxes."""
        inc_id_str = str(incident_id)
        snap_id = f"SNAP_{inc_id_str}_{frame_number}_{int(datetime.now().timestamp())}"
        filename = f"{snap_id}.jpg"
        file_path = self.snapshot_dir / filename

        annotated = image.copy() if image is not None else np.zeros((480, 640, 3), dtype=np.uint8)
        if bounding_boxes and image is not None:
            for box in bounding_boxes:
                if len(box) >= 4:
                    x1, y1, x2, y2 = map(int, box[:4])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(
                        annotated,
                        "TARGET EVIDENCE",
                        (x1, max(y1 - 5, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1,
                    )

        cv2.imwrite(str(file_path), annotated)

        return SnapshotMetadata(
            snapshot_id=snap_id,
            incident_id=inc_id_str,
            camera_id=str(camera_id),
            frame_number=int(frame_number),
            trigger_reason=str(trigger_reason),
            file_path=str(file_path),
            file_uri=f"/api/evidence/snapshots/file/{filename}",
        )

    def save_multi_evidence_package(
        self,
        incident_id: Union[str, UUID],
        image: np.ndarray,
        camera_id: str = "CAM-01",
        frame_number: int = 0,
        trigger_reason: str = "RESTRICTED_ZONE_BREACH",
        bounding_boxes: Optional[List[List[float]]] = None,
        face_bbox: Optional[List[float]] = None,
        plate_bbox: Optional[List[float]] = None,
        confidence: float = 0.9,
        modality: str = "STANDARD",
    ) -> EvidencePackageMetadata:
        """
        Generate and persist Full Scene Evidence + Face Evidence Crop + ANPR Plate Crop.
        """
        inc_id_str = str(incident_id)
        snap_meta = self.save_snapshot(
            incident_id=inc_id_str,
            image=image,
            camera_id=str(camera_id),
            frame_number=int(frame_number),
            trigger_reason=str(trigger_reason),
            bounding_boxes=bounding_boxes,
            modality=modality,
        )

        face_uri = None
        plate_uri = None
        sharpness = BestEvidenceFrameSelector.calculate_sharpness(image)

        if image is not None and image.size > 0:
            h, w = image.shape[:2]

            # 1. Face Evidence Snapshot Crop
            if face_bbox and len(face_bbox) >= 4:
                fx1, fy1, fx2, fy2 = map(int, face_bbox[:4])
                fx1, fy1 = max(0, fx1), max(0, fy1)
                fx2, fy2 = min(w, fx2), min(h, fy2)
                if fx2 > fx1 and fy2 > fy1:
                    face_crop = image[fy1:fy2, fx1:fx2]
                    face_fname = f"FACE_{snap_meta.snapshot_id}.jpg"
                    face_fpath = self.snapshot_dir / face_fname
                    cv2.imwrite(str(face_fpath), face_crop)
                    face_uri = f"/api/evidence/snapshots/file/{face_fname}"

            # 2. ANPR License Plate Evidence Crop
            if plate_bbox and len(plate_bbox) >= 4:
                px1, py1, px2, py2 = map(int, plate_bbox[:4])
                px1, py1 = max(0, px1), max(0, py1)
                px2, py2 = min(w, px2), min(h, py2)
                if px2 > px1 and py2 > py1:
                    plate_crop = image[py1:py2, px1:px2]
                    plate_fname = f"ANPR_{snap_meta.snapshot_id}.jpg"
                    plate_fpath = self.snapshot_dir / plate_fname
                    cv2.imwrite(str(plate_fpath), plate_crop)
                    plate_uri = f"/api/evidence/snapshots/file/{plate_fname}"

        return EvidencePackageMetadata(
            snapshot_id=snap_meta.snapshot_id,
            incident_id=inc_id_str,
            camera_id=str(camera_id),
            frame_number=int(frame_number),
            trigger_reason=str(trigger_reason),
            file_path=snap_meta.file_path,
            file_uri=snap_meta.file_uri,
            face_snapshot_uri=face_uri,
            anpr_snapshot_uri=plate_uri,
            sharpness_score=round(sharpness, 1),
            confidence=float(confidence),
            modality=modality,
        )

    save_snapshot_with_crops = save_multi_evidence_package

    async def save_snapshot_async(
        self,
        incident_id: Union[str, UUID],
        image: np.ndarray,
        camera_id: str = "CAM-01",
        frame_number: int = 0,
        trigger_reason: str = "RESTRICTED_ZONE_BREACH",
        bounding_boxes: Optional[List[List[float]]] = None,
        modality: str = "STANDARD",
    ) -> SnapshotMetadata:
        """Asynchronously save a snapshot offloaded to worker thread to prevent event-loop stalls."""
        import asyncio
        return await asyncio.to_thread(
            self.save_snapshot,
            incident_id=incident_id,
            image=image,
            camera_id=camera_id,
            frame_number=frame_number,
            trigger_reason=trigger_reason,
            bounding_boxes=bounding_boxes,
            modality=modality,
        )

    async def save_multi_evidence_package_async(
        self,
        incident_id: Union[str, UUID],
        image: np.ndarray,
        camera_id: str = "CAM-01",
        frame_number: int = 0,
        trigger_reason: str = "RESTRICTED_ZONE_BREACH",
        bounding_boxes: Optional[List[List[float]]] = None,
        face_bbox: Optional[List[float]] = None,
        plate_bbox: Optional[List[float]] = None,
        confidence: float = 0.9,
        modality: str = "STANDARD",
    ) -> EvidencePackageMetadata:
        """Asynchronously generate and persist full + face + ANPR evidence package."""
        import asyncio
        return await asyncio.to_thread(
            self.save_multi_evidence_package,
            incident_id=incident_id,
            image=image,
            camera_id=camera_id,
            frame_number=frame_number,
            trigger_reason=trigger_reason,
            bounding_boxes=bounding_boxes,
            face_bbox=face_bbox,
            plate_bbox=plate_bbox,
            confidence=confidence,
            modality=modality,
        )

    def list_snapshots(self, incident_id: Union[str, UUID]) -> List[SnapshotMetadata]:
        results = []
        inc_id_str = str(incident_id)
        for file in self.snapshot_dir.glob(f"SNAP_{inc_id_str}_*.jpg"):
            results.append(
                SnapshotMetadata(
                    snapshot_id=file.stem,
                    incident_id=incident_id,
                    camera_id="UNKNOWN",
                    frame_number=0,
                    trigger_reason="HISTORICAL",
                    file_path=str(file),
                    file_uri=f"/api/evidence/snapshots/file/{file.name}",
                )
            )
        return results


global_snapshot_manager = SnapshotArchiveManager()


def get_snapshot_manager() -> SnapshotArchiveManager:
    return global_snapshot_manager
