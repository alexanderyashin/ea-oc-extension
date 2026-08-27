from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "DOWNSTREAM_REVALIDATION_REPORT_v1.json"
FIXTURE = ROOT / "DOWNSTREAM_REVALIDATION_FIXTURE_v1.json"
PACKET = ROOT / "DOWNSTREAM_COMPATIBILITY_PACKET_v1.json"
MATRIX = ROOT / "CANDIDATE_TO_CLAIM_MATRIX_v1.json"
FREEZE = ROOT / "CANDIDATE_FREEZE_MANIFEST_v1.json"


CURRENT_REFS = {
    "WS-60-TOOLKIT": {"repository":"estra-toolkit","branch":"workstream/oc14-toolkit-luna-20260827","commit":"137f7733febf6c026619816272f9440e0d029f3c","tree":"cdece84101752f68c7e1d85f734c406c2190bd8f"},
    "WS-75-PUBLICATION": {"repository":"Logion","branch":"workstream/oc14-publication-luna-20260827","commit":"cd1149108fdc4c02b6a019f369b4fb8ef582b616","tree":"98d7e74c7698d77fad775de21fb309a2c277d0fe"},
}


def verdict(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def evaluate(scenario: dict) -> dict[str, str]:
    refs = scenario["consumer_refs"]
    for consumer, expected in CURRENT_REFS.items():
        actual = refs.get(consumer)
        if actual is None or actual["commit"] != expected["commit"] or actual["tree"] != expected["tree"]:
            return verdict("BLOCKED_CONSUMER_COMPATIBILITY", "WS60_REJECT_STALE_CONSUMER_REF")
        if actual["repository"] != expected["repository"] or actual["branch"] != expected["branch"]:
            return verdict("BLOCKED_CONSUMER_COMPATIBILITY", "WS60_REJECT_PROVENANCE_MISMATCH")
    path = scenario["candidate_path"]
    if path.startswith("/") or ":\\" in path or "Private/" in path or "/Runtime/" in path:
        return verdict("BLOCKED_CONSUMER_COMPATIBILITY", "WS75_REJECT_PRIVATE_RUNTIME_PATH")
    context = scenario.get("claim_context", {})
    if context.get("requested_claim") == "typed-history-dominance":
        return verdict("BLOCKED_CLAIM_CEILING", "WS60_REJECT_WIDENED_CLAIM_CEILING")
    return verdict("PASS_READ_ONLY_REVALIDATION", "CURRENT_CONSUMER_REFS_MATCH")


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    rows = report["candidate_rows"]
    assert len(rows) == 40 == len(matrix["rows"]) == len(freeze["files"])
    packet_by_path = {row["path"]: row for row in packet["candidate_rows"]}
    matrix_by_path = {row["path"]: row for row in matrix["rows"]}
    freeze_by_path = {row["path"]: row for row in freeze["files"]}
    assert {row["path"] for row in rows} == set(packet_by_path) == set(matrix_by_path) == set(freeze_by_path)
    for consumer, expected in CURRENT_REFS.items():
        assert {key: report["current_consumer_refs"][consumer][key] for key in expected} == expected
        assert fixture["current_consumer_refs"][consumer] == expected
    for row in rows:
        path = row["path"]
        assert row["semantic_digest"] == freeze_by_path[path]["sha256"]
        assert row["candidate_state"] == matrix_by_path[path]["semantic_status"]
        assert row["rejection_profile"] == packet_by_path[path]["compatibility_profile"]
    outputs = []
    for scenario in fixture["scenarios"]:
        actual = evaluate(scenario)
        assert actual == scenario["expected"], (scenario["id"], actual, scenario["expected"])
        outputs.append({"id": scenario["id"], **actual})
    assert outputs[0]["status"] == "PASS_READ_ONLY_REVALIDATION"
    assert all(item["status"] == "BLOCKED_CONSUMER_COMPATIBILITY" for item in outputs[1:4])
    assert outputs[4]["status"] == "BLOCKED_CLAIM_CEILING"
    print(json.dumps({"status":"PASS_DOWNSTREAM_REVALIDATION","candidate_rows":40,"scenarios":len(outputs),"results":outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
