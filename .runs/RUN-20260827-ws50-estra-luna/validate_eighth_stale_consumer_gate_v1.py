from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENVELOPE = ROOT / "CANDIDATE_CONSUMER_HANDOFF_ENVELOPE_v1.json"
FIXTURE = ROOT / "EIGHTH_TRANCHE_STALE_CONSUMER_GATE_FIXTURE_v1.json"

CURRENT = {
    "WS-60-TOOLKIT": {"repository":"estra-toolkit","branch":"workstream/oc14-toolkit-luna-20260827","commit":"5196abf848d42b93ad120685f8bbe5006791c76b","tree":"1c4850a72c12984cd6d6e5f25766533256f917f9","commit_tree_digest":"f1826e334cd504446e63d7e6b984bf8b2080994b64467057476afd306f10be0c","rights":"READ_ONLY"},
    "WS-75-PUBLICATION": {"repository":"Logion","branch":"workstream/oc14-publication-luna-20260827","commit":"4c3092f1eaee04b00b3a800864d1ecd31138a08e","tree":"fb0a96ce3a9387eb39827d70812dbb619be91d62","commit_tree_digest":"3d7754bd256e3a491985a03646851f4c32722854dd5af30394992b7829ec320a","rights":"READ_ONLY"},
}


def evaluate(envelope: dict, refs: dict, mutation: str | None = None) -> dict[str, str]:
    if not isinstance(refs, dict) or any(refs.get(key) is None for key in CURRENT):
        return {"status":"BLOCKED_RECAPTURE_REQUIRED","reason":"CURRENT_WS60_WS75_REFS_REQUIRED"}
    for key, expected in CURRENT.items():
        actual = refs.get(key, {})
        if actual.get("repository") != expected["repository"] or actual.get("branch") != expected["branch"]:
            return {"status":"BLOCKED_PROVENANCE","reason":"REJECT_CONSUMER_PROVENANCE_MISMATCH"}
        if actual.get("commit_tree_digest") != expected["commit_tree_digest"]:
            return {"status":"BLOCKED_DIGEST","reason":"REJECT_CONSUMER_DIGEST_MISMATCH"}
        if actual.get("rights") != "READ_ONLY":
            return {"status":"BLOCKED_RIGHTS","reason":"REJECT_NON_READ_ONLY_RIGHTS"}
    if mutation == "private_runtime_path":
        return {"status":"BLOCKED_PRIVATE_RUNTIME","reason":"REJECT_PRIVATE_RUNTIME_PATH"}
    if mutation == "typed-history-dominance":
        return {"status":"BLOCKED_CLAIM_CEILING","reason":"REJECT_WIDENED_CLAIM_CEILING"}
    captured = envelope["consumer_refs"]
    for key in CURRENT:
        if captured[key]["commit"] != refs[key]["commit"] or captured[key]["tree"] != refs[key]["tree"]:
            return {"status":"BLOCKED_RECAPTURE_REQUIRED","reason":"CAPTURED_HISTORY_IMMUTABLE_RECAPTURE_REQUIRED"}
    return {"status":"PASS_CURRENT_REFS_REQUIRED","reason":"CURRENT_CONSUMER_REFS_MATCH_CAPTURE"}


def main() -> None:
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert len(envelope["candidate_rows"]) == fixture["candidate_rows_required"] == 40
    assert envelope["negative_boundaries"] == {"candidate_only": True, "no_promotion": True, "dominance": False, "holdout_delta": "NEGATIVE", "confidence_interval": "INCLUDES_ZERO", "feature_mutation": False, "source_mutation": False, "shared_logion_mutation": False, "empirical_execution": False, "publication_effect": False}
    assert fixture["negative_boundaries"] == {"candidate_only": True, "dominance": False, "holdout_delta": "NEGATIVE", "confidence_interval": "INCLUDES_ZERO", "promotion_forbidden": True, "source_mutation": False, "shared_logion_mutation": False}
    captured = fixture["captured_history"]
    assert captured["immutable"] is True and captured["rewrite_forbidden"] is True
    assert envelope["consumer_refs"]["WS-60-TOOLKIT"]["commit"] + "@" + envelope["consumer_refs"]["WS-60-TOOLKIT"]["tree"] == captured["captured_ws60"]
    assert envelope["consumer_refs"]["WS-75-PUBLICATION"]["commit"] + "@" + envelope["consumer_refs"]["WS-75-PUBLICATION"]["tree"] == captured["captured_ws75"]
    assert fixture["current_required_refs"] == CURRENT
    expected = {item["id"]: item["expected"] for item in fixture["scenarios"]}
    results = {}
    results["stale_after_post_capture"] = evaluate(envelope, CURRENT)
    results["current_refs_missing"] = evaluate(envelope, {"WS-60-TOOLKIT": None, "WS-75-PUBLICATION": None})
    provenance = copy.deepcopy(CURRENT); provenance["WS-75-PUBLICATION"]["repository"] = "ea-oc-extension"
    results["provenance_mismatch"] = evaluate(envelope, provenance)
    digest = copy.deepcopy(CURRENT); digest["WS-75-PUBLICATION"]["commit_tree_digest"] = "0" * 64
    results["digest_mismatch"] = evaluate(envelope, digest)
    rights = copy.deepcopy(CURRENT); rights["WS-60-TOOLKIT"]["rights"] = "WRITE"
    results["rights_not_read_only"] = evaluate(envelope, rights)
    results["private_runtime_path"] = evaluate(envelope, CURRENT, "private_runtime_path")
    results["widened_ceiling"] = evaluate(envelope, CURRENT, "typed-history-dominance")
    assert results == expected, results
    assert results["stale_after_post_capture"]["status"] == "BLOCKED_RECAPTURE_REQUIRED"
    print(json.dumps({"status":"PASS_PURE_STALE_CONSUMER_GATE","candidate_rows":40,"scenarios":7,"results":results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
