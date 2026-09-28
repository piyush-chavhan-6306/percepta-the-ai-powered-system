"""
Border Intelligence Security Zones & Virtual Boundaries REST API.
Provides endpoints for creating, listing, and managing spatial security zones and virtual tripwires.
"""
from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.zones.security_zone import (
    SecurityZone,
    VirtualBoundary,
    ZoneSeverity,
    get_zone_monitor,
)

router = APIRouter(prefix="/api/zones", tags=["Security Zones"])


class CreateZoneRequest(BaseModel):
    zone_id: Optional[str] = None
    name: str
    polygon: List[Tuple[float, float]] = Field(..., min_length=3, description="List of (x, y) coordinates")
    severity: str = "restricted"  # "info", "warning", "restricted", "critical"
    camera_id: Optional[str] = None
    loitering_threshold_seconds: Optional[float] = 2.0
    loitering_debounce_seconds: float = 30.0


class CreateBoundaryRequest(BaseModel):
    boundary_id: Optional[str] = None
    name: str
    pt1: Tuple[float, float]
    pt2: Tuple[float, float]
    severity: str = "critical"
    direction: str = "BIDIRECTIONAL"  # "NORTH", "SOUTH", "EAST", "WEST", "BIDIRECTIONAL"
    camera_id: Optional[str] = None
    debounce_seconds: float = 3.0


class ZoneResponse(BaseModel):
    zone_id: str
    name: str
    polygon: List[Tuple[float, float]]
    severity: str
    is_active: bool
    camera_id: Optional[str] = None
    loitering_threshold_seconds: Optional[float] = None


class BoundaryResponse(BaseModel):
    boundary_id: str
    name: str
    pt1: Tuple[float, float]
    pt2: Tuple[float, float]
    severity: str
    direction: str = "BIDIRECTIONAL"
    is_active: bool
    camera_id: Optional[str] = None


class ZoneListResponse(BaseModel):
    zones: List[ZoneResponse]
    boundaries: List[BoundaryResponse]


@router.get("", response_model=ZoneListResponse)
async def list_zones_and_boundaries(camera_id: Optional[str] = None) -> ZoneListResponse:
    """List all active security zones and virtual tripwire boundaries (optionally filtered by camera_id)."""
    monitor = get_zone_monitor()
    raw_zones = monitor.zones.values()
    raw_boundaries = monitor.boundaries.values()

    if camera_id:
        raw_zones = [z for z in raw_zones if not getattr(z, "camera_id", None) or z.camera_id == camera_id]
        raw_boundaries = [b for b in raw_boundaries if not getattr(b, "camera_id", None) or b.camera_id == camera_id]

    zones_list = [
        ZoneResponse(
            zone_id=z.zone_id,
            name=z.name,
            polygon=z.polygon,
            severity=z.severity.value,
            is_active=z.is_active,
            camera_id=getattr(z, "camera_id", None),
            loitering_threshold_seconds=z.loitering_threshold_seconds,
        )
        for z in raw_zones
    ]
    boundaries_list = [
        BoundaryResponse(
            boundary_id=b.boundary_id,
            name=b.name,
            pt1=b.pt1,
            pt2=b.pt2,
            severity=b.severity.value,
            direction=getattr(b, "direction", "BIDIRECTIONAL"),
            is_active=b.is_active,
            camera_id=getattr(b, "camera_id", None),
        )
        for b in raw_boundaries
    ]
    return ZoneListResponse(zones=zones_list, boundaries=boundaries_list)


@router.post("", response_model=ZoneResponse)
async def create_security_zone(request: CreateZoneRequest) -> ZoneResponse:
    """Create a new polygon security zone."""
    monitor = get_zone_monitor()
    sev = ZoneSeverity.from_str(request.severity)

    import uuid
    zid = request.zone_id or f"zone_{uuid.uuid4().hex[:8]}"

    zone = SecurityZone(
        zone_id=zid,
        name=request.name,
        polygon=request.polygon,
        severity=sev,
        camera_id=request.camera_id,
        loitering_threshold_seconds=request.loitering_threshold_seconds,
        loitering_debounce_seconds=request.loitering_debounce_seconds,
    )
    monitor.add_zone(zone)
    return ZoneResponse(
        zone_id=zone.zone_id,
        name=zone.name,
        polygon=zone.polygon,
        severity=zone.severity.value,
        is_active=zone.is_active,
        camera_id=zone.camera_id,
        loitering_threshold_seconds=zone.loitering_threshold_seconds,
    )


@router.post("/boundary", response_model=BoundaryResponse)
@router.post("/boundaries", response_model=BoundaryResponse)
async def create_virtual_boundary(request: CreateBoundaryRequest) -> BoundaryResponse:
    """Create a new virtual tripwire boundary line."""
    import uuid
    monitor = get_zone_monitor()
    sev = ZoneSeverity.from_str(request.severity)

    boundary_id = request.boundary_id or f"boundary-{uuid.uuid4().hex[:8]}"
    boundary = VirtualBoundary(
        boundary_id=boundary_id,
        name=request.name,
        pt1=request.pt1,
        pt2=request.pt2,
        severity=sev,
        direction=request.direction,
        camera_id=request.camera_id,
        debounce_seconds=request.debounce_seconds,
    )
    monitor.add_boundary(boundary)
    return BoundaryResponse(
        boundary_id=boundary.boundary_id,
        name=boundary.name,
        pt1=boundary.pt1,
        pt2=boundary.pt2,
        severity=boundary.severity.value,
        direction=boundary.direction,
        is_active=boundary.is_active,
        camera_id=boundary.camera_id,
    )


@router.delete("/{zone_id}")
async def delete_zone_or_boundary(zone_id: str) -> Dict[str, Any]:
    """Delete a security zone or virtual boundary."""
    monitor = get_zone_monitor()
    if monitor.remove_zone(zone_id):
        return {"zone_id": zone_id, "status": "deleted", "type": "zone"}
    if monitor.remove_boundary(zone_id):
        return {"zone_id": zone_id, "status": "deleted", "type": "boundary"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Zone or boundary '{zone_id}' not found",
    )


@router.get("/templates")
async def get_zone_templates():
    """Retrieve standard tactical security zone and virtual tripwire templates."""
    from backend.zones.templates import list_tactical_templates
    return {"templates": list_tactical_templates()}


@router.post("/apply-template")
async def apply_zone_template(request: dict):
    """Instantiate a tactical template into the active surveillance zone monitor."""
    from backend.zones.templates import apply_tactical_template
    tmpl_id = request.get("template_id")
    suffix = request.get("zone_id_suffix", "01")
    custom_name = request.get("custom_name")

    if not tmpl_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'template_id' is required",
        )
    try:
        res = apply_tactical_template(template_id=tmpl_id, custom_name=custom_name, zone_id_suffix=suffix)
        return res
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
