"""Checkpoint persistence matching ACP spec."""
import json
import os
import gzip
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_DIR = Path(os.environ.get("ATLAS_DATA_DIR", ".atlas"))


class Checkpoint:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.checkpoints_dir = self.data_dir / "checkpoints"
        self.runs_dir = self.data_dir / "runs"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, checkpoint_data, level="standard"):
        checkpoint_id = f"cp-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
        checkpoint_data["checkpointId"] = checkpoint_id
        checkpoint_data["level"] = level
        checkpoint_data["created"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        cp_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        with open(cp_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)
        
        if level == "deep":
            context_path = self.checkpoints_dir / f"{checkpoint_id}.context.gz"
            # dummy context
            with gzip.open(context_path, "wb") as f:
                f.write(b"{}")
        
        return checkpoint_id
    
    def load(self, checkpoint_id):
        cp_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        if not cp_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        with open(cp_path) as f:
            return json.load(f)
    
    def list(self, run_id=None):
        checkpoints = []
        for cp_file in self.checkpoints_dir.glob("cp-*.json"):
            try:
                with open(cp_file) as f:
                    data = json.load(f)
                if run_id is None or data.get("runId") == run_id:
                    checkpoints.append(data)
            except Exception:
                continue
        return sorted(checkpoints, key=lambda x: x.get("created", ""))
    
    def fork(self, checkpoint_id, fork_level="resume"):
        data = self.load(checkpoint_id)
        if fork_level == "replay":
            return data  # same data
        elif fork_level == "branch":
            data["runId"] = f"run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-branch"
            return self.save(data)
        elif fork_level == "resume":
            return checkpoint_id  # continue from existing
        raise ValueError(f"Unknown fork level: {fork_level}")
