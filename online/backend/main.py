"""
Border Intelligence Main FastAPI Application.
Initializes lifespan lifecycle, database connections, event bus, API gateway, and REST/WebSocket routers.
"""
import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent
_online_root = _backend_dir.parent
if str(_online_root) not in sys.path:
    sys.path.insert(0, str(_online_root))

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.winmm.timeBeginPeriod(1)
    except Exception:
        pass

import cv2
try:
    cv2.ocl.setUseOpenCL(False)
except Exception:
    pass

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from backend.api.alerts import router as alerts_router
from backend.api.cameras import DEFAULT_DEMO_CLIP, resolve_video_path, router as cameras_router
from backend.api.events import router as events_router
from backend.api.export import router as export_router
from backend.api.forensics import router as forensics_router
from backend.api.health import router as health_router
from backend.api.incidents import router as incidents_router
from backend.api.intelligence import router as intelligence_router
from backend.api.pathguard import router as pathguard_router
from backend.api.sensors import router as sensors_router
from backend.api.streaming import router as streaming_router
from backend.api.system import router as system_router
from backend.api.threat import router as threat_router
from backend.api.zones import router as zones_router
from backend.config import get_settings
from backend.database import close_db, init_db, init_cloud_db
from backend.events.schema import SourceType
from backend.gateway.auth import router as auth_router
from backend.gateway.middleware import GatewaySecurityMiddleware, log_gateway_startup_banner
from backend.gateway.rate_limit import limiter, rate_limit_exceeded_handler
from backend.ingestion.camera_manager import get_camera_manager
from backend.ingestion.video_adapter import VideoFileAdapter
from backend.tracking.live_worker import get_worker_registry

try:
    from backend.api.upload import router as upload_router
except ImportError:
    from online.backend.api.upload import router as upload_router

try:
    from sync.receiver import router as sync_router
except ImportError:
    from online.sync.receiver import router as sync_router

try:
    from services.queue_manager import get_queue_manager
except ImportError:
    from online.services.queue_manager import get_queue_manager

logger = logging.getLogger(__name__)

DEMO_CAMERA_ID = "CAM-01"


async def bootstrap_demo_camera(autostart: bool = False) -> None:
    """
    Register default surveillance cameras only if explicitly enabled.
    Disabled by default so the system starts with a clean camera registry.
    """
    settings = get_settings()
    if not settings.AUTOSTART_DEMO_CAMERA:
        logger.info("Demo camera auto-registration disabled. Starting with empty operator registry.")
        return

    configs = [
        ("CAM-01", "Border Post Alpha (Optical CCTV - Demo)", "Sector 7 Perimeter", "STANDARD", clip),
    ]
    clip2 = resolve_video_path("border-demo.mp4") or clip
    if clip2:
        configs.append(("CAM-02", "Border Post Bravo (Thermal IR - Demo)", "Sector 4 Ridge", "THERMAL", clip2))

    for item in configs:
        cid, name, loc, mod, vpath = item
        if manager.get_camera(cid) is not None:
            continue
        try:
            adapter = VideoFileAdapter(
                camera_id=cid,
                video_path=vpath,
                loop=True,
                modality=mod,
            )
            manager.register_camera(
                camera_id=cid,
                adapter=adapter,
                name=name,
                location_label=loc,
                modality=mod,
                source_type=SourceType.VIDEO_FILE,
            )
            if autostart:
                if await manager.start_camera(cid):
                    await get_worker_registry().start_worker(cid)
                    logger.info(f"Multi-Modal Camera '{cid}' [{mod}] live on {vpath}")
                else:
                    await manager.deregister_camera(cid)
            else:
                logger.info(f"Registered camera '{cid}' in STANDBY mode (ready for operator activation).")
        except Exception as err:
            logger.warning(f"Camera bootstrap failed for {cid}: {err}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown lifecycle."""
    settings = get_settings()
    settings.ensure_directories()

    # 1. Initialize SQLite Database with WAL mode
    await init_db()

    # Initialize Neon Cloud Schema if configured
    try:
        await init_cloud_db()
    except Exception as e:
        logger.warning(f"Cloud DB initialization skipped/deferred: {e}")

    # Initialize Online Queue Manager
    try:
        queue_mgr = get_queue_manager()
        queue_mgr.start()
    except Exception as e:
        logger.warning(f"Queue manager initialization skipped/deferred: {e}")

    # 2. Log Gateway Status Banner
    log_gateway_startup_banner()

    # 3. Register default camera in inventory (standby by default)
    await bootstrap_demo_camera(autostart=settings.AUTOSTART_DEMO_CAMERA)

    yield

    # 4. Stop queue manager, perception workers before their sources, then close the database.
    try:
        queue_mgr = get_queue_manager()
        await queue_mgr.stop()
    except Exception:
        pass
    await get_worker_registry().stop_all()
    manager = get_camera_manager()
    await manager.stop_all()
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application with Gateway Security."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Persistent AI Intelligence Layer for Border Surveillance (SIH Prototype)",
        version=settings.API_VERSION,
        lifespan=lifespan,
    )

    # Attach Gateway Rate Limiter state and error handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Attach Gateway Security & Telemetry Middleware
    app.add_middleware(GatewaySecurityMiddleware)

    # CORS configuration for frontend dashboard
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Gateway Auth Router
    app.include_router(auth_router)

    # Register Domain Routers
    app.include_router(health_router)
    app.include_router(events_router)
    app.include_router(intelligence_router)
    app.include_router(threat_router)
    app.include_router(forensics_router)
    app.include_router(cameras_router)
    app.include_router(alerts_router)
    app.include_router(incidents_router)
    app.include_router(zones_router)
    app.include_router(pathguard_router)
    app.include_router(export_router)
    app.include_router(sensors_router)
    app.include_router(system_router)
    app.include_router(streaming_router)
    app.include_router(upload_router)
    app.include_router(sync_router)

    @app.get("/health")
    async def root_health():
        return {"status": "healthy", "service": "percepta-online-backend"}

    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "status": "online",
            "docs_url": "/docs",
            "health_url": "/api/health",
            "auth_status": "demo_mode" if settings.DEMO_MODE else "strict_jwt",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
