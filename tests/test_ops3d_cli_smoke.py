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

def test_validate_prints_ok_or_stop(tmp_path: Path):
    # minimal JSON spec (does not assume any particular schema)
    spec = tmp_path / "s.json"
    spec.write_text('{"x": 1}', encoding="utf-8")

    r = run(["validate", str(spec)])
    # Accept either:
    # - OK (0) if core hook exists
    # - STOP (2) if hook missing / validation not available
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
