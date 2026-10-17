"""Trust profile persistence (ARTS scores)."""
import json
import os
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_DIR = Path(os.environ.get("ATLAS_DATA_DIR", ".atlas"))


class TrustProfiles:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.profiles_path = self.data_dir / "trust-profiles.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.profiles = self._load()
    
    def _load(self):
        if self.profiles_path.exists():
            try:
                with open(self.profiles_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save(self):
        with open(self.profiles_path, "w") as f:
            json.dump(self.profiles, f, indent=2)
    
    def get(self, role):
        return self.profiles.get(role, {
            "trustScore": 0.5,
            "tier": "STANDARD",
            "qualityAvg": 0.5,
            "criticPassRate": 0.5,
            "reworkRate": 0.5,
            "escalationRate": 0.5,
            "taskCount": 0,
            "lastUsed": datetime.utcnow().strftime('%Y-%m-%d'),
            "lastQualityScore": 0.5,
            "driftAlerts": 0,
            "trend": "stable"
        })
    
    def update(self, role, quality_score):
        prof = self.get(role)
        prof["qualityAvg"] = (prof["qualityAvg"] * prof["taskCount"] + quality_score) / (prof["taskCount"] + 1) if prof["taskCount"] > 0 else quality_score
        prof["taskCount"] += 1
        prof["lastUsed"] = datetime.utcnow().strftime('%Y-%m-%d')
        prof["lastQualityScore"] = quality_score
        # simple trust calculation
        prof["trustScore"] = min(1.0, max(0.0, prof["qualityAvg"]))
        if prof["trustScore"] >= 0.8:
            prof["tier"] = "TRUSTED"
        elif prof["trustScore"] >= 0.6:
            prof["tier"] = "STANDARD"
        elif prof["trustScore"] >= 0.3:
            prof["tier"] = "PROBATION"
        else:
            prof["tier"] = "UNTRUSTED"
        self.profiles[role] = prof
        self.save()
        return prof
