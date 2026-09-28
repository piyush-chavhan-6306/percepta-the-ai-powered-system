"""
PERCEPTA OFFLINE PERSISTENT SYNC QUEUE
Stores sync items in SQLite so state survives application restart.
Provides background worker for automatic upload when Internet is detected.
"""
import asyncio
from datetime import datetime, timezone
import json
import logging
import sqlite3
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger("percepta.offline.sync")


class PersistentSyncQueue:
    def __init__(self, db_path: str = "./percepta_sync.db", cloud_api_url: str = "http://localhost:8000"):
        self.db_path = db_path
        self.cloud_api_url = cloud_api_url.rstrip("/")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    sync_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    source_device_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'PENDING',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_state ON sync_queue (state);")
            conn.commit()
        finally:
            conn.close()

    def enqueue(self, sync_id: str, entity_type: str, entity_id: str, source_device_id: str, payload: Dict[str, Any]) -> str:
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR REPLACE INTO sync_queue
                (sync_id, entity_type, entity_id, source_device_id, payload, state, retry_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'PENDING', 0, ?, ?)
            """, (sync_id, entity_type, entity_id, source_device_id, json.dumps(payload), now, now))
            conn.commit()
        finally:
            conn.close()
        logger.info(f"Enqueued {entity_type} {entity_id} [sync_id: {sync_id}]")
        return sync_id

    def get_pending_items(self, limit: int = 25) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sync_queue WHERE state IN ('PENDING', 'RETRYING') ORDER BY created_at ASC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def mark_state(self, sync_id: str, state: str, error: Optional[str] = None):
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            if error:
                conn.execute(
                    "UPDATE sync_queue SET state = ?, last_error = ?, retry_count = retry_count + 1, updated_at = ? WHERE sync_id = ?",
                    (state, error, now, sync_id)
                )
            else:
                conn.execute(
                    "UPDATE sync_queue SET state = ?, last_error = NULL, updated_at = ? WHERE sync_id = ?",
                    (state, now, sync_id)
                )
            conn.commit()
        finally:
            conn.close()

    async def check_connectivity(self) -> bool:
        """Check if Cloud API / Internet is reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.cloud_api_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    async def sync_once(self) -> int:
        """Process pending queue items when internet is available."""
        if not await self.check_connectivity():
            return 0

        items = self.get_pending_items()
        synced_count = 0
        async with httpx.AsyncClient(timeout=10.0) as client:
            for item in items:
                sync_id = item["sync_id"]
                self.mark_state(sync_id, "UPLOADING")
                try:
                    payload = json.loads(item["payload"])
                    endpoint = f"{self.cloud_api_url}/api/sync/packet"
                    resp = await client.post(endpoint, json={
                        "sync_id": sync_id,
                        "entity_type": item["entity_type"],
                        "entity_id": item["entity_id"],
                        "source_device_id": item["source_device_id"],
                        "payload": payload,
                    })
                    if resp.status_code in (200, 201):
                        self.mark_state(sync_id, "SYNCED")
                        synced_count += 1
                    else:
                        self.mark_state(sync_id, "RETRYING", f"HTTP {resp.status_code}: {resp.text[:100]}")
                except Exception as ex:
                    self.mark_state(sync_id, "RETRYING", str(ex))
        return synced_count
