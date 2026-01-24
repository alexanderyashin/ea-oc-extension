import argparse
from pathlib import Path
from ops3d_cli.policy import *
from ops3d_cli.spec_io import load_spec

def _lazy_core():
    try:
        import ops3a_engine
        return ops3a_engine, None
    except Exception as e:
        return None, Stop("Core import failed", str(e))

def main(argv=None):
    import sys
    argv = sys.argv[1:] if argv is None else argv

    if (s := detect_forbidden_semantics(argv)):
        print(s.format())
        return STOP_EXIT_CODE

    p = argparse.ArgumentParser(prog="ops3d")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate")
    v.add_argument("spec")

    d = sub.add_parser("diagnose")
    d.add_argument("spec")
    d.add_argument("--data")
    d.add_argument("--dump-trace")
    d.add_argument("--dump-graph")

    ns = p.parse_args(argv)

    spec = load_spec(ns.spec)
    if isinstance(spec, Stop):
        print(spec.format())
        return STOP_EXIT_CODE

    core, err = _lazy_core()
    if err:
        print(err.format())
        return STOP_EXIT_CODE

    if ns.cmd == "validate":
        if not hasattr(core, "validate_spec"):
            print("STOP: validate_spec hook missing")
            return STOP_EXIT_CODE
        ok, report = core.validate_spec(spec.obj)
        print("OK" if ok else f"STOP: {report}")
        return END_EXIT_CODE if ok else STOP_EXIT_CODE

    if ns.cmd == "diagnose":
        if not hasattr(core, "diagnose"):
            print("STOP: diagnose hook missing")
            return STOP_EXIT_CODE
        result = core.diagnose(spec.obj, ns.data, {})
        print(result.get("status", "STOP"))
        return END_EXIT_CODE if result.get("status") == "END" else STOP_EXIT_CODE
