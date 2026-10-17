"""Main orchestrator enforcing state machine."""
from atlas_runtime import state, workflow, checkpoint, dag, anomaly, token_budget, trust
import os
from pathlib import Path


class Orchestrator:
    def __init__(self, data_dir=None):
        self.checkpointer = checkpoint.Checkpoint(data_dir)
        self.trust_profiles = trust.TrustProfiles(data_dir)
        self.anomaly_detector = anomaly.AnomalyDetector()
        self.token_counter = token_budget.TokenCounter()
        self.run_id = None
        self.phases = {}
    
    def load_workflow(self, workflow_name, variant="full"):
        fm, text = workflow.load_workflow(workflow_name)
        self.workflow_fm = fm
        self.workflow_text = text
        self.variant = variant
        return fm
    
    def initialize_phases(self):
        phases = self.workflow_fm.get("phases", [])
        if not phases:
            # derive from text if needed - simple approach
            pass
        for p in phases:
            name = p.get("name") if isinstance(p, dict) else str(p)
            phase = state.PhaseState(
                name,
                roles=p.get("roles", []) if isinstance(p, dict) else [],
                gate=p.get("gate") if isinstance(p, dict) else None,
                parallel=p.get("parallel", False) if isinstance(p, dict) else False
            )
            self.phases[name] = phase
    
    def run_phase(self, phase_name):
        if phase_name not in self.phases:
            raise KeyError(f"Unknown phase: {phase_name}")
        phase = self.phases[phase_name]
        if not phase.can_transition("active"):
            raise ValueError(f"Cannot activate phase {phase_name} from {phase.state}")
        phase.transition("active")
        return phase
    
    def complete_phase(self, phase_name, deliverables=None):
        if phase_name not in self.phases:
            raise KeyError(f"Unknown phase: {phase_name}")
        phase = self.phases[phase_name]
        phase.deliverables = deliverables or []
        phase.transition("gated")
        return phase
    
    def approve_phase(self, phase_name):
        if phase_name not in self.phases:
            raise KeyError(f"Unknown phase: {phase_name}")
        phase = self.phases[phase_name]
        phase.transition("completed")
        return phase
    
    def fail_phase(self, phase_name, error=""):
        if phase_name not in self.phases:
            raise KeyError(f"Unknown phase: {phase_name}")
        phase = self.phases[phase_name]
        phase.errors.append(error)
        phase.transition("failed")
        return phase
    
    def save_checkpoint(self, level="standard"):
        checkpoint_data = {
            "runId": self.run_id or "run-unknown",
            "phase": list(self.phases.values())[0].phase_name if self.phases else "none",
            "variant": self.variant,
            "context": {
                "phases": {name: p.state for name, p in self.phases.items()}
            }
        }
        return self.checkpointer.save(checkpoint_data, level=level)
