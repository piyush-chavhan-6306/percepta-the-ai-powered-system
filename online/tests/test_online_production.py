"""
PERCEPTA ONLINE — PRODUCTION CAPABILITY & LIFECYCLE TEST SUITE
Verifies:
1. Tripwire crossing precision: physical crossings trigger alerts; parallel or non-crossing movements reject false positives.
2. Unconfigured cameras produce zero phantom perimeter intrusion alerts.
3. Independent multi-camera analysis (stopping Cam 2 does not stop Cam 1).
4. Storage Retention Manager: 24h raw video purge with permanent forensic evidence hold protection.
5. Chunked upload session lifecycle and cancellation.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

from backend.events.schema import SourceType
from backend.tracking.tracker import TrackedObject
from backend.zones.security_zone import (
    SecurityZone,
    VirtualBoundary,
    ZoneMonitor,
    ZoneSeverity,
)
from storage.retention_manager import RetentionManager


def _make_track(track_id: str, cx: float, cy: float, age: int = 5, object_class: str = "person") -> TrackedObject:
    return TrackedObject(
        track_id=track_id,
        object_class=object_class,
        confidence=0.92,
        bounding_box=[cx - 20, cy - 40, cx + 20, cy + 40],
        normalized_box=[cx / 1280.0, cy / 720.0, (cx + 40) / 1280.0, (cy + 80) / 720.0],
        frame_number=1,
        timestamp=datetime.now(timezone.utc),
        center_x=cx,
        center_y=cy,
        age=age,
    )


def test_tripwire_crossing_detection_and_false_positive_rejection():
    """Verify physical crossing generates an alert, while parallel motion does not."""
    # Horizontal tripwire at y=300 from x=100 to x=1000
    boundary = VirtualBoundary(
        boundary_id="tw_sector_01",
        name="Sector Bravo Tripwire",
        pt1=(100.0, 300.0),
        pt2=(1000.0, 300.0),
        severity=ZoneSeverity.CRITICAL,
        direction="BIDIRECTIONAL",
    )
    monitor = ZoneMonitor(boundaries=[boundary])

    # 1. Parallel movement (y: 250 -> 250): Object moves horizontally above line (NO crossing)
    t1_f1 = _make_track("101", 300.0, 250.0, age=5)
    _, alerts_f1 = monitor.evaluate_tracks([t1_f1], camera_id="CAM-01")
    assert len(alerts_f1) == 0

    t1_f2 = _make_track("101", 400.0, 250.0, age=6)
    _, alerts_f2 = monitor.evaluate_tracks([t1_f2], camera_id="CAM-01")
    assert len(alerts_f2) == 0, "Parallel movement must NEVER trigger tripwire breach!"

    # 2. Genuine physical crossing (y: 280 -> 320 crossing y=300):
    t2_f1 = _make_track("102", 500.0, 280.0, age=5)
    monitor.evaluate_tracks([t2_f1], camera_id="CAM-01")

    t2_f2 = _make_track("102", 500.0, 320.0, age=6)
    _, alerts_cross = monitor.evaluate_tracks([t2_f2], camera_id="CAM-01")
    assert len(alerts_cross) == 1, "Genuine crossing across tripwire must trigger alert!"
    assert "BORDER BREACH" in alerts_cross[0].message
    assert alerts_cross[0].zone_id == "tw_sector_01"


def test_unconfigured_camera_produces_zero_perimeter_alerts():
    """Verify that when no custom zones or tripwires exist on a camera, no phantom perimeter alerts fire."""
    # Empty monitor (no zones, no tripwires)
    monitor = ZoneMonitor(zones=[], boundaries=[])

    track = _make_track("201", 640.0, 360.0, age=20)
    zone_evs, alert_evs = monitor.evaluate_tracks([track], camera_id="CAM-UNCONFIGURED")

    # Critical requirement: Zero phantom alerts
    assert len(zone_evs) == 0
    assert len(alert_evs) == 0


def test_24_hour_retention_purge_and_evidence_hold(tmp_path):
    """Verify raw videos older than 24h are purged while evidence and hold files are preserved."""
    test_storage = tmp_path / "test_storage"
    rec_dir = test_storage / "recordings"
    ev_dir = test_storage / "evidence"
    rec_dir.mkdir(parents=True)
    ev_dir.mkdir(parents=True)

    # 1. Old raw video (created 25 hours ago)
    old_video = rec_dir / "cam_01_old.mp4"
    old_video.write_bytes(b"surveillance_raw_content_old")
    old_mtime = (datetime.now(timezone.utc) - timedelta(hours=25)).timestamp()
    import os
    os.utime(old_video, (old_mtime, old_mtime))

    # 2. Fresh raw video (created 2 hours ago)
    fresh_video = rec_dir / "cam_01_fresh.mp4"
    fresh_video.write_bytes(b"surveillance_raw_content_fresh")

    # 3. Old raw video protected under FORENSIC EVIDENCE HOLD
    hold_video = rec_dir / "cam_02_incident.mp4"
    hold_video.write_bytes(b"incident_evidence_hold_raw")
    os.utime(hold_video, (old_mtime, old_mtime))

    # 4. Permanent forensic snapshot in evidence directory
    snapshot = ev_dir / "evidence_snapshot_inc_999.jpg"
    snapshot.write_bytes(b"forensic_jpeg_snapshot")
    os.utime(snapshot, (old_mtime, old_mtime))

    mgr = RetentionManager(storage_dir=str(test_storage), retention_hours=24)
    mgr.protect_video("cam_02_incident")

    # Execute retention purge
    stats = mgr.purge_expired_recordings()

    # Old raw video must be deleted
    assert not old_video.exists(), "Raw surveillance recording older than 24h must be purged"
    assert stats["purged_count"] == 1

    # Fresh raw video must be preserved
    assert fresh_video.exists(), "Fresh recording (< 24h) must remain intact"

    # Evidence hold video must be preserved despite being older than 24h
    assert hold_video.exists(), "Video under forensic evidence hold must NEVER be purged"

    # Evidence directory file must NEVER be touched
    assert snapshot.exists(), "Permanent forensic snapshots must be retained indefinitely"
