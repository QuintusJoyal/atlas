"""Enforceable state machine for workflow phases."""

STATES = {
    "pending",
    "active",
    "gated",
    "completed",
    "failed",
    "paused",
    "aborted",
}

TRANSITIONS = {
    ("pending", "active"),
    ("active", "gated"),
    ("gated", "completed"),
    ("gated", "failed"),
    ("active", "failed"),
    ("any", "aborted"),
    ("active", "paused"),
    ("paused", "active"),
    ("paused", "aborted"),
}

class PhaseState:
    def __init__(self, phase_name, roles=None, gate=None, parallel=False):
        self.phase_name = phase_name
        self.roles = roles or []
        self.gate = gate
        self.parallel = parallel
        self.state = "pending"
        self.deliverables = []
        self.errors = []
    
    def can_transition(self, new_state):
        if self.state == new_state:
            return True
        if (self.state, new_state) in TRANSITIONS:
            return True
        if ("any", new_state) in TRANSITIONS:
            return True
        return False
    
    def transition(self, new_state):
        if not self.can_transition(new_state):
            raise ValueError(f"Invalid transition {self.state} -> {new_state}")
        self.state = new_state
