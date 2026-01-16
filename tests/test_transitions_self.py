from ea_oc_ext.guards.transitions import TransitionContext, is_transition_allowed


def test_self_transition_allowed_for_non_stop():
    ctx = TransitionContext(external_psi_restores_potentials=False)
    assert is_transition_allowed("SUCCESS", "SUCCESS", ctx) is True
    assert is_transition_allowed("INERTIA", "INERTIA", ctx) is True
    assert is_transition_allowed("COLLAPSE", "COLLAPSE", ctx) is True


def test_self_transition_not_allowed_for_stop():
    ctx = TransitionContext(external_psi_restores_potentials=False)
    assert is_transition_allowed("STOP", "STOP", ctx) is False
