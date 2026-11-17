import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    """Har test ko apna alag SQLite DB — cache/counters leak nahi hote."""
    monkeypatch.setenv("SS_DB_PATH", str(tmp_path / "test.db"))
    yield
