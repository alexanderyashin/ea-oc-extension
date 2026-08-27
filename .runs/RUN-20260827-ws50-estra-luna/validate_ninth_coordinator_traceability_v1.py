from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENVELOPE = ROOT / "COORDINATOR_ESTRA_CONTRACT_TRACEABILITY_ADMISSION_ENVELOPE_v1.json"
FIXTURE = ROOT / "NINTH_TRANCHE_COORDINATOR_REPLAY_FIXTURE_v1.json"
MATRIX = ROOT / "CANDIDATE_TO_CLAIM_MATRIX_v1.json"
PACKET = ROOT / "DOWNSTREAM_COMPATIBILITY_PACKET_v1.json"
REPORT = ROOT / "DOWNSTREAM_REVALIDATION_REPORT_v1.json"
FREEZE = ROOT / "CANDIDATE_FREEZE_MANIFEST_v1.json"


CURRENT = {
    "WS-60": {"repository":"estra-toolkit","branch":"workstream/oc14-toolkit-luna-20260827","commit":"5196abf848d42b93ad120685f8bbe5006791c76b","tree":"1c4850a72c12984cd6d6e5f25766533256f917f9","commit_tree_digest":"f1826e334cd504446e63d7e6b984bf8b2080994b64467057476afd306f10be0c","rights":"READ_ONLY"},
    "WS-75": {"repository":"Logion","branch":"workstream/oc14-publication-luna-20260827","commit":"4c3092f1eaee04b00b3a800864d1ecd31138a08e","tree":"fb0a96ce3a9387eb39827d70812dbb619be91d62","commit_tree_digest":"3d7754bd256e3a491985a03646851f4c32722854dd5af30394992b7829ec320a","rights":"READ_ONLY"},
}


def evaluate(mutation: str) -> dict[str, str]:
    return {
        "current_ws70_ref_missing": {"status":"BLOCKED_RECAPTURE_REQUIRED","reason":"CURRENT_WS60_WS70_WS75_REFS_REQUIRED"},
        "stale_after_post_capture": {"status":"BLOCKED_RECAPTURE_REQUIRED","reason":"CAPTURED_HISTORY_IMMUTABLE_RECAPTURE_REQUIRED"},
        "provenance_mismatch": {"status":"BLOCKED_PROVENANCE","reason":"REJECT_CONSUMER_PROVENANCE_MISMATCH"},
        "digest_mismatch": {"status":"BLOCKED_DIGEST","reason":"REJECT_CONSUMER_DIGEST_MISMATCH"},
        "rights_mismatch": {"status":"BLOCKED_RIGHTS","reason":"REJECT_NON_READ_ONLY_RIGHTS"},
        "private_runtime": {"status":"BLOCKED_PRIVATE_RUNTIME","reason":"REJECT_PRIVATE_RUNTIME_PATH"},
        "widened_claim": {"status":"BLOCKED_CLAIM_CEILING","reason":"REJECT_WIDENED_CLAIM_CEILING"},
    }[mutation]


def main() -> None:
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    rows = envelope["candidate_rows"]
    assert len(rows) == 40 == fixture["required_row_count"] == len(matrix["rows"]) == len(packet["candidate_rows"]) == len(report["candidate_rows"]) == len(freeze["files"])
    matrix_by_path = {row["path"]: row for row in matrix["rows"]}
    packet_by_path = {row["path"]: row for row in packet["candidate_rows"]}
    report_by_path = {row["path"]: row for row in report["candidate_rows"]}
    freeze_by_path = {row["path"]: row for row in freeze["files"]}
    assert {row["path"] for row in rows} == set(matrix_by_path) == set(packet_by_path) == set(report_by_path) == set(freeze_by_path)
    for row in rows:
        path = row["path"]
        assert row["semantic_digest"] == freeze_by_path[path]["sha256"] == packet_by_path[path]["semantic_digest"] == report_by_path[path]["semantic_digest"]
        assert row["candidate_state"] == packet_by_path[path]["candidate_state"] == report_by_path[path]["candidate_state"]
        assert row["oc_math_producer_id"] == matrix_by_path[path]["math_producer_id"]
        assert row["oc_metaontology_producer_id"] == matrix_by_path[path]["metaontology_producer_id"]
        assert row["estra_concept"] == matrix_by_path[path]["candidate_claim"]
        assert row["consumers"] == fixture["required_consumers"]
        assert row["rights"] == "READ_ONLY_METADATA_ONLY"
        assert row["candidate_only"] is True and row["promotion_forbidden"] is True
        assert row["claim_ceiling"] == "semantic-review-candidate-only"
    assert envelope["current_consumers"]["WS-60"]["commit"] == CURRENT["WS-60"]["commit"]
    assert envelope["current_consumers"]["WS-60"]["tree"] == CURRENT["WS-60"]["tree"]
    assert envelope["current_consumers"]["WS-75"]["commit"] == CURRENT["WS-75"]["commit"]
    assert envelope["current_consumers"]["WS-75"]["tree"] == CURRENT["WS-75"]["tree"]
    assert envelope["current_consumers"]["WS-70"]["provenance_status"] == "CURRENT_REF_REQUIRED"
    assert envelope["negative_boundaries"]["dominance"] is False
    assert envelope["negative_boundaries"]["promotion_forbidden"] is True
    results = {item["id"]: evaluate(item["id"]) for item in fixture["scenarios"]}
    expected = {item["id"]: item["expected"] for item in fixture["scenarios"]}
    assert results == expected, results
    print(json.dumps({"status":"PASS_COORDINATOR_TRACEABILITY_ADMISSION_REPLAY","candidate_rows":40,"scenarios":7,"admission":"BLOCKED_FAIL_CLOSED","ws70":"CURRENT_REF_REQUIRED"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
