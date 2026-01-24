import subprocess
import sys
from pathlib import Path

STOP = 2

def run(args):
    return subprocess.run(
        [sys.executable, "-m", "ops3d_cli", *args],
        capture_output=True,
        text=True,
    )

def test_unknown_command_exitcode_nonzero():
    r = run(["unknowncmd"])
    assert r.returncode != 0

def test_invalid_spec_stop(tmp_path: Path):
    r = run(["validate", str(tmp_path / "missing.yaml")])
    assert r.returncode == STOP
    out = (r.stdout + r.stderr)
    assert "STOP" in out

def test_forbidden_semantics_flag_stop():
    # forbidden semantics must trigger STOP even if other args are nonsense
    r = run(["validate", "missing.yaml", "--optimize"])
    assert r.returncode == STOP
    assert "Forbidden CLI semantics" in (r.stdout + r.stderr)

def test_no_state_persistence_across_runs(tmp_path: Path):
    # CLI must not create state files by default.
    spec = tmp_path / "s.json"
    spec.write_text('{"x": 1}', encoding="utf-8")

    before = set(p.name for p in tmp_path.iterdir())
    r1 = run(["validate", str(spec)])
    mid = set(p.name for p in tmp_path.iterdir())
    r2 = run(["validate", str(spec)])
    after = set(p.name for p in tmp_path.iterdir())

    assert before == mid == after
    assert r1.returncode in (0, STOP)
    assert r2.returncode in (0, STOP)
