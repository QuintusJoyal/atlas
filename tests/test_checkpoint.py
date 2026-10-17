from atlas_runtime import checkpoint
import tempfile
import os

def test_checkpoint_save_load():
    with tempfile.TemporaryDirectory() as tmp:
        cp = checkpoint.Checkpoint(data_dir=tmp)
        cid = cp.save({"runId": "test-123", "phase": "impl"}, level="standard")
        loaded = cp.load(cid)
        assert loaded["runId"] == "test-123"
        assert loaded["level"] == "standard"
