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

def test_validate_prints_ok_or_stop(tmp_path: Path):
    spec = tmp_path / "s.json"
    spec.write_text('{"x": 1}', encoding="utf-8")

    r = run(["validate", str(spec)])
    assert r.returncode in (0, STOP)

    out = (r.stdout + r.stderr)
    assert ("OK" in out) or ("STOP" in out)

def test_diagnose_ends_or_stops_cleanly(tmp_path: Path):
    spec = tmp_path / "s.json"
    spec.write_text('{"x": 1}', encoding="utf-8")

    r = run(["diagnose", str(spec)])
    assert r.returncode in (0, STOP)

    out = (r.stdout + r.stderr)
    assert ("END" in out) or ("STOP" in out)
