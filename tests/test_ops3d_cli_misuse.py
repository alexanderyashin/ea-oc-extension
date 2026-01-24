import os
import subprocess
import sys
from pathlib import Path

STOP = 2

def run(args):
    # Ensure src-layout imports work inside the subprocess (no global state)
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_path) + ((";" + existing) if existing else "")

    return subprocess.run(
        [sys.executable, "-m", "ops3d_cli", *args],
        capture_output=True,
        text=True,
        env=env,
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
    r = run(["validate", "missing.yaml", "--optimize"])
    assert r.returncode == STOP
    assert "Forbidden CLI semantics" in (r.stdout + r.stderr)

def test_no_state_persistence_across_runs(tmp_path: Path):
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
