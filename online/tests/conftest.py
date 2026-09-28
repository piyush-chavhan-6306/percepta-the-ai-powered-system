"""
Pytest configuration for PERCEPTA test suite.
Isolates test runs to an independent test database so tests never pollute operational surveillance data.
"""
import os
import sys
from pathlib import Path
import pytest

# Ensure online root and backend are in sys.path
_test_dir = Path(__file__).resolve().parent
_online_root = _test_dir.parent
for _p in (str(_online_root), str(_online_root / "backend")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Enforce isolated test database before any backend modules are imported
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_percepta.db"
os.environ["DEMO_MODE"] = "true"
os.environ["PERCEPTA_ENV"] = "test"


@pytest.fixture(scope="session", autouse=True)
def clean_test_database():
    """Ensure test database is cleaned up after test run."""
    yield
    for fname in ["test_percepta.db", "test_percepta.db-wal", "test_percepta.db-shm"]:
        if os.path.exists(fname):
            try:
                os.remove(fname)
            except Exception:
                pass
