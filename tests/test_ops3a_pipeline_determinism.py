import copy
import pytest

from src.ops3c_integration.adapter import IntegrationWrapper


def _trace_fingerprint(trace) -> str:
    """
    Deterministic fingerprint for comparison.

    We prefer the wrapper envelope hash because:
      - it is stable
      - it is independent of object identity/repr
      - it is the pipeline-level determinism evidence required by C.3
    """
    if isinstance(trace, dict) and "ops3c_envelope_hash" in trace:
        return str(trace["ops3c_envelope_hash"])
    return str(trace)


@pytest.mark.parametrize("spec", [
    {"edges": [["A", "B"], ["B", "C"]]},
    {"graph": {"edges": [{"from": "X", "to": "Y"}]}},
])
def test_pipeline_determinism_same_input_same_trace(spec):
    """
    C.3: identical pipeline (core primitives + wrapper) ⇒ identical trace fingerprint.
    We compare wrapper-enveloped traces (envelope hash).
    """
    w1 = IntegrationWrapper(registered_extensions={"ext_ok"})
    w2 = IntegrationWrapper(registered_extensions={"ext_ok"})

    # extensions payload object identity must not affect determinism
    extensions1 = {"ext_ok": object()}
    extensions2 = {"ext_ok": object()}

    r1 = w1.run(copy.deepcopy(spec), extensions=extensions1)
    r2 = w2.run(copy.deepcopy(spec), extensions=extensions2)

    assert _trace_fingerprint(r1.trace) == _trace_fingerprint(r2.trace)


def test_pipeline_nondeterminism_attempt_detected_at_boundary():
    """
    Any attempt to inject nondeterminism into spec must hard-fail at boundary.
    """
    w = IntegrationWrapper(registered_extensions=set())
    with pytest.raises(Exception):
        w.run({"edges": [["A", "B"]], "random": 123})
