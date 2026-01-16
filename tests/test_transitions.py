from ea_oc_ext.guards.transitions import TransitionContext, is_transition_allowed, guard_transition_or_stop


def test_inertia_to_success_requires_external_psi():
    ctx0 = TransitionContext(external_psi_restores_potentials=False)
    ctx1 = TransitionContext(external_psi_restores_potentials=True)
    assert is_transition_allowed("INERTIA", "SUCCESS", ctx0) is False
    assert is_transition_allowed("INERTIA", "SUCCESS", ctx1) is True


def test_collapse_to_success_forbidden():
    ctx = TransitionContext(external_psi_restores_potentials=True)
    assert is_transition_allowed("COLLAPSE", "SUCCESS", ctx) is False
    assert guard_transition_or_stop("COLLAPSE", "SUCCESS", ctx) == "STOP"


def test_stop_terminal():
    ctx = TransitionContext(external_psi_restores_potentials=True)
    assert is_transition_allowed("STOP", "SUCCESS", ctx) is False
    assert guard_transition_or_stop("STOP", "SUCCESS", ctx) == "STOP"
