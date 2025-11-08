import pytest
from datasourcelib.core.sync_manager import SyncManager
from datasourcelib.core.sync_types import SyncType

def test_full_sync_runs(tmp_path):
    sm = SyncManager()
    src = {"connection": "dummy"}
    vec = {"endpoint": "dummy"}
    res = sm.execute_sync(SyncType.FULL, source_config=src, vector_db_config=vec)
    assert res["status"] is not None