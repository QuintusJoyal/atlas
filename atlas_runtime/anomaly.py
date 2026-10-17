"""Stuck-agent detection - 6 anomaly types."""
from collections import Counter, defaultdict


class AnomalyDetector:
    def __init__(self):
        self.errors = []
        self.trajectory = []
    
    def add_entry(self, entry):
        self.trajectory.append(entry)
    
    def detect(self):
        anomalies = []
        # 1. Repeater - same error 3+ times from same role
        errors_by_role = defaultdict(Counter)
        for t in self.trajectory:
            if t.get("outcome") == "failure" and t.get("error"):
                role = t.get("role", "unknown")
                errors_by_role[role][t["error"]] += 1
        for role, errors in errors_by_role.items():
            for err, count in errors.items():
                if count >= 3:
                    anomalies.append({
                        "type": "repeater",
                        "role": role,
                        "error": err,
                        "count": count
                    })
        
        # 2. Looper - cycle detected
        reasons_by_role = defaultdict(Counter)
        for t in self.trajectory:
            if t.get("why"):
                role = t.get("role", "unknown")
                reasons_by_role[role][t["why"]] += 1
        for role, reasons in reasons_by_role.items():
            for reason, count in reasons.items():
                if count >= 3:
                    anomalies.append({
                        "type": "looper",
                        "role": role,
                        "reason": reason,
                        "count": count
                    })
        
        # 3. Escalation Storm - 3+ escalations
        escalations = sum(1 for t in self.trajectory if t.get("outcome") == "escalated")
        if escalations >= 3:
            anomalies.append({
                "type": "escalation_storm",
                "count": escalations
            })
        
        return anomalies
