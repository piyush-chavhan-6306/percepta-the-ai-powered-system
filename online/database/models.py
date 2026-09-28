"""
PERCEPTA ONLINE DATABASE MODELS (Neon PostgreSQL / Cloud Storage)
Implements all metadata models specified in Rules 9 & 10 with strict user/tenant isolation.
"""
from datetime import datetime, timezone
import uuid
from typing import Optional, List
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
try:
    from database.neon_adapter import Base
except ImportError:
    from online.database.neon_adapter import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class UserModel(Base):
    """Authenticated user registry synced from Supabase Auth."""
    __tablename__ = "online_users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Supabase sub UUID
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(64), default="SURVEILLANCE_OFFICER")
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    profile: Mapped[Optional["ProfileModel"]] = relationship("ProfileModel", back_populates="user", uselist=False)
    cameras: Mapped[List["CameraModel"]] = relationship("CameraModel", back_populates="user")


class ProfileModel(Base):
    """Officer dossier and professional clearance profile."""
    __tablename__ = "online_profiles"

    profile_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("online_users.user_id"), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="Duty Officer")
    rank: Mapped[str] = mapped_column(String(128), default="Tactical Operator")
    gender: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    regiment: Mapped[str] = mapped_column(String(128), default="Northern Command")
    division: Mapped[str] = mapped_column(String(128), default="Border Surveillance Unit")
    organization: Mapped[str] = mapped_column(String(128), default="Border Intelligence Force")
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clearance_level: Mapped[str] = mapped_column(String(64), default="LEVEL-4")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")


class CameraModel(Base):
    """Camera stream configurations and operational status."""
    __tablename__ = "online_cameras"

    camera_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("online_users.user_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), default="video_file")  # video_file, rtsp, ip_camera
    source_uri: Mapped[str] = mapped_column(Text, nullable=False)
    camera_type: Mapped[str] = mapped_column(String(32), default="RGB")  # RGB, IR, THERMAL
    location: Mapped[str] = mapped_column(String(255), default="Sector 7 Perimeter")
    status: Mapped[str] = mapped_column(String(32), default="ONLINE")  # ONLINE, OFFLINE, STANDBY
    trust_score: Mapped[float] = mapped_column(Float, default=95.0)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="cameras")
    incidents: Mapped[List["OnlineIncidentModel"]] = relationship("OnlineIncidentModel", back_populates="camera")


class OnlineIncidentModel(Base):
    """Centralized incident lifecycle record."""
    __tablename__ = "online_incidents"

    incident_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g., INC-2026-001
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    camera_id: Mapped[str] = mapped_column(String(64), ForeignKey("online_cameras.camera_id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    incident_type: Mapped[str] = mapped_column(String(64), default="RESTRICTED_ZONE_VIOLATION")
    threat_severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")  # NORMAL, RESTRICTED, CRITICAL
    threat_score: Mapped[float] = mapped_column(Float, default=70.0)
    lifecycle: Mapped[str] = mapped_column(String(32), default="DETECTED")  # DETECTED, ACTIVE, ACKNOWLEDGED, RESOLVED, HISTORICAL
    primary_track_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    global_object_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    zone_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    camera: Mapped["CameraModel"] = relationship("CameraModel", back_populates="incidents")
    alerts: Mapped[List["OnlineAlertModel"]] = relationship("OnlineAlertModel", back_populates="incident")
    evidence: Mapped[List["OnlineEvidenceModel"]] = relationship("OnlineEvidenceModel", back_populates="incident")


class OnlineAlertModel(Base):
    """Discrete security alerts triggered by incidents or sensor events."""
    __tablename__ = "online_alerts"

    alert_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(64), ForeignKey("online_incidents.incident_id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    track_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    threat_severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")
    threat_score: Mapped[float] = mapped_column(Float, default=70.0)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    incident: Mapped["OnlineIncidentModel"] = relationship("OnlineIncidentModel", back_populates="alerts")


class OnlineEvidenceModel(Base):
    """Cryptographic Triple-A Evidence metadata."""
    __tablename__ = "online_evidence"

    evidence_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(64), ForeignKey("online_incidents.incident_id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(64), default="image/jpeg")
    file_uri: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    is_permanent: Mapped[bool] = mapped_column(Boolean, default=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    incident: Mapped["OnlineIncidentModel"] = relationship("OnlineIncidentModel", back_populates="evidence")


class ZoneModel(Base):
    """Perimeter geofences and restricted security zones."""
    __tablename__ = "online_zones"

    zone_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    polygon_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON normalized coordinates [[x,y],...]
    severity: Mapped[str] = mapped_column(String(32), default="RESTRICTED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TripwireModel(Base):
    """Directional virtual tripwires."""
    __tablename__ = "online_tripwires"

    boundary_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    pt1_json: Mapped[str] = mapped_column(String(64), nullable=False)
    pt2_json: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[str] = mapped_column(String(32), default="BIDIRECTIONAL")
    severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CameraTrustModel(Base):
    """Historical and active Camera Trust Sensor reports."""
    __tablename__ = "online_camera_trust"

    trust_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    trust_score: Mapped[float] = mapped_column(Float, nullable=False)
    trust_level: Mapped[str] = mapped_column(String(32), nullable=False)
    factors_json: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class PathGuardEventModel(Base):
    """Route integrity breaches and corridor deviations."""
    __tablename__ = "online_pathguard_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    track_id: Mapped[str] = mapped_column(String(64), nullable=False)
    corridor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    deviation_distance: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DEVIATION_DETECTED")
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class BlindSpotMetadataModel(Base):
    """Perimeter coverage analysis, blind spot detection, and uncertainty estimates."""
    __tablename__ = "online_blind_spots"

    blind_spot_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    camera_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sector_name: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")
    coverage_gap_ratio: Mapped[float] = mapped_column(Float, default=0.5)
    uncertainty: Mapped[str] = mapped_column(String(32), default="LOW")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CopilotRecordModel(Base):
    """Audit log of natural-language grounded intelligence interactions."""
    __tablename__ = "online_copilot_records"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    tools_called_json: Mapped[str] = mapped_column(Text, default="[]")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SyncRecordModel(Base):
    """Edge-to-cloud synchronization transaction journal with idempotency keys."""
    __tablename__ = "online_sync_records"

    sync_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_device_id: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMMITTED")
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AuditLogModel(Base):
    """Immutable audit trail for security compliance and operator actions."""
    __tablename__ = "online_audit_logs"

    log_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    details: Mapped[str] = mapped_column(Text, default="{}")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
