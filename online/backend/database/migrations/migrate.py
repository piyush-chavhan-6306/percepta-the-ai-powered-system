"""
PERCEPTA ONLINE — DATABASE MIGRATION SCRIPT
Initializes and updates Neon PostgreSQL schema tables for online multi-tenant C2.
Tables: users, profiles, cameras, camera_configs, incidents, alerts, tracking_metadata,
zones, tripwires, camera_trust, pathguard_events, blind_spot_metadata, copilot_records,
sync_records, audit_logs.
"""
import asyncio
import os
import sys
from pathlib import Path

# Ensure online root is in sys.path
_current = Path(__file__).resolve().parent
_root = _current.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

try:
    from database.neon_adapter import init_cloud_db, get_neon_database_url
except ImportError:
    from online.database.neon_adapter import init_cloud_db, get_neon_database_url


async def run_migrations(db_url: str | None = None) -> None:
    url = db_url or get_neon_database_url()
    print(f"[MIGRATION] Connecting to database: {url.split('@')[-1] if '@' in url else url}")
    engine = await init_cloud_db(url)
    print("[MIGRATION] All 14 PERCEPTA Online tables successfully initialized.")
    await engine.dispose()


if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_migrations(db_url))
