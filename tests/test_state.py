from atlas_runtime import state

def test_phase_transitions():
    p = state.PhaseState("test")
    assert p.state == "pending"
    assert p.can_transition("active")
    p.transition("active")
    p.transition("gated")
    p.transition("completed")
