from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "DOWNSTREAM_COMPATIBILITY_PACKET_v1.json"
FIXTURE = ROOT / "DOWNSTREAM_COMPATIBILITY_FIXTURE_v1.json"
MATRIX = ROOT / "CANDIDATE_TO_CLAIM_MATRIX_v1.json"
FREEZE = ROOT / "CANDIDATE_FREEZE_MANIFEST_v1.json"


def verdict(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def evaluate(scenario: dict, contract: dict) -> dict[str, str]:
    refs = scenario["consumer_refs"]
    code_prefix = {"WS-60-TOOLKIT": "WS60", "WS-75-PUBLICATION": "WS75"}
    for consumer, expected in contract.items():
        prefix = code_prefix[consumer]
        actual = refs.get(consumer)
        if actual is None:
            return verdict("BLOCKED_CONSUMER_COMPATIBILITY", f"{prefix}_REJECT_MISSING_CONSUMER_REF")
        if actual["commit"] != expected["commit"] or actual["tree"] != expected["tree"]:
            return verdict("BLOCKED_CONSUMER_COMPATIBILITY", f"{prefix}_REJECT_STALE_CONSUMER_REF")
        if actual["repository"] != expected["repository"] or actual["branch"] != expected["branch"]:
            return verdict("BLOCKED_CONSUMER_COMPATIBILITY", f"{prefix}_REJECT_PROVENANCE_MISMATCH")

    path = scenario["candidate_path"]
    if path.startswith("/") or ":\\" in path or "Private/" in path or "/Runtime/" in path:
        return verdict("BLOCKED_CONSUMER_COMPATIBILITY", "WS75_REJECT_PRIVATE_RUNTIME_PATH")
    context = scenario.get("claim_context", {})
    if context.get("requested_claim") == "typed-history-dominance":
        return verdict("BLOCKED_CLAIM_CEILING", "WS60_REJECT_WIDENED_CLAIM_CEILING")
    return verdict("PASS_DOWNSTREAM_COMPATIBILITY_REVIEW_ONLY", "ACCEPT_READ_ONLY_CURRENT_CONSUMER_REFS")


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    packet_rows = packet["candidate_rows"]
    matrix_rows = matrix["rows"]
    freeze_rows = freeze["files"]
    assert len(packet_rows) == 40 == len(matrix_rows) == len(freeze_rows)
    matrix_by_path = {row["path"]: row for row in matrix_rows}
    freeze_by_path = {row["path"]: row for row in freeze_rows}
    assert {row["path"] for row in packet_rows} == set(matrix_by_path) == set(freeze_by_path)
    for row in packet_rows:
        path = row["path"]
        assert row["semantic_digest"] == freeze_by_path[path]["sha256"]
        assert row["candidate_state"] == matrix_by_path[path]["semantic_status"]
        assert row["source_commit"] == freeze["source_checkout_head"]
        assert row["source_tree"] == freeze["source_checkout_tree"]
        assert row["compatibility_profile"] in packet["compatibility_profiles"]
        profile = packet["compatibility_profiles"][row["compatibility_profile"]]
        expected_codes = [code for codes in profile["expected_consumer_rejection_codes"].values() for code in codes]
        assert row["toolkit_expectation"] == profile["toolkit_expectation"]
        assert row["publication_expectation"] == profile["publication_expectation"]
        assert row["expected_consumer_rejection_codes"] == expected_codes
    outputs = []
    contract = fixture["consumer_ref_contract"]
    for scenario in fixture["scenarios"]:
        actual = evaluate(scenario, contract)
        assert actual == scenario["expected"], (scenario["id"], actual, scenario["expected"])
        outputs.append({"id": scenario["id"], **actual})
    assert outputs[0]["status"] == "PASS_DOWNSTREAM_COMPATIBILITY_REVIEW_ONLY"
    assert all(item["status"] == "BLOCKED_CONSUMER_COMPATIBILITY" for item in outputs[1:4])
    assert outputs[4]["status"] == "BLOCKED_CLAIM_CEILING"
    print(json.dumps({"status":"PASS_DOWNSTREAM_COMPATIBILITY","candidate_rows":40,"scenarios":len(outputs),"results":outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
