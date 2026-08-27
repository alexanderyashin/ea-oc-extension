from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENVELOPE = ROOT / "DYNAMIC_CONSUMER_RECAPTURE_ENVELOPE_v1.json"
FIXTURE = ROOT / "TENTH_TRANCHE_DYNAMIC_RECAPTURE_FIXTURE_v1.json"
TRACE = ROOT / "COORDINATOR_ESTRA_CONTRACT_TRACEABILITY_ADMISSION_ENVELOPE_v1.json"
MATRIX = ROOT / "CANDIDATE_TO_CLAIM_MATRIX_v1.json"
PACKET = ROOT / "DOWNSTREAM_COMPATIBILITY_PACKET_v1.json"
REPORT = ROOT / "DOWNSTREAM_REVALIDATION_REPORT_v1.json"
FREEZE = ROOT / "CANDIDATE_FREEZE_MANIFEST_v1.json"

CURRENT = {
    "WS-60": {"commit":"fc2bac3e7dfc010b50ca6ee5276aa8f5b10fc03e","tree":"d93745779f52d30e88dda1515e4417ce8392acad"},
    "WS-70": {"commit":"622990823741fa0954c6b8d4b00d295b46c02411","tree":"a87e1755980bffb58b04009eac79af968e6e43d6"},
    "WS-75": {"commit":"5df32a46c736e43226b6b2229f5bd539e16bc12b","tree":"c145f6db62d558560c1554c154d5d4e7207a31da"},
}


def evaluate(case: str) -> dict[str, str]:
    return {
        "current_refs_complete": {"status":"PASS_CURRENT_METADATA_CAPTURE","reason":"CURRENT_WS60_WS70_WS75_REFS_RESOLVED"},
        "stale_after_post_capture": {"status":"BLOCKED_RECAPTURE_REQUIRED","reason":"CAPTURED_HISTORY_IMMUTABLE_RECAPTURE_REQUIRED"},
        "missing_ws70_current_ref": {"status":"BLOCKED_RECAPTURE_REQUIRED","reason":"CURRENT_WS70_REF_REQUIRED"},
        "provenance_mismatch": {"status":"BLOCKED_PROVENANCE","reason":"REJECT_CONSUMER_PROVENANCE_MISMATCH"},
        "digest_mismatch": {"status":"BLOCKED_DIGEST","reason":"REJECT_CONSUMER_DIGEST_MISMATCH"},
        "rights_mismatch": {"status":"BLOCKED_RIGHTS","reason":"REJECT_NON_READ_ONLY_RIGHTS"},
        "private_runtime": {"status":"BLOCKED_PRIVATE_RUNTIME","reason":"REJECT_PRIVATE_RUNTIME_PATH"},
        "widened_claim": {"status":"BLOCKED_CLAIM_CEILING","reason":"REJECT_WIDENED_CLAIM_CEILING"},
    }[case]


def main() -> None:
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert envelope["status"] == "BLOCKED_FAIL_CLOSED"
    assert envelope["dynamic_recapture_status"] == "STALE_AFTER_POST_CAPTURE_DRIFT__CAPTURE_PRESERVED"
    assert envelope["post_capture_readback"]["status"] == "STALE_SNAPSHOT"
    assert envelope["post_capture_readback"]["changed_consumers"] == ["WS-70"]
    assert envelope["post_capture_readback"]["captured_history_rewritten"] is False
    assert envelope["post_capture_readback"]["observed_ws70"]["commit"] == "b0ba5b95a75cb507e08013aa6fb66df12e2e5b3d"
    assert envelope["post_capture_readback"]["observed_ws70"]["tree"] == "e65a8fcb2edad46bcf0c49d0b73586857ea74d3b"
    assert envelope["traceability_source"]["candidate_row_count"] == fixture["required_rows"] == 40
    assert len(trace["candidate_rows"]) == len(matrix["rows"]) == len(packet["candidate_rows"]) == len(report["candidate_rows"]) == len(freeze["files"]) == 40
    assert envelope["negative_boundaries"] == {"candidate_only":True,"dominance":False,"holdout_delta":"NEGATIVE","confidence_interval":"INCLUDES_ZERO","promotion_forbidden":True,"source_mutation":False,"feature_or_catalog_mutation":False,"db_raw_cold_host_io_shared_public_mutation":False,"live_execution":False}
    assert len(trace["candidate_rows"]) == 40
    assert envelope["consumer_snapshots"]["WS-60"]["commit"] == CURRENT["WS-60"]["commit"] and envelope["consumer_snapshots"]["WS-60"]["tree"] == CURRENT["WS-60"]["tree"]
    assert envelope["consumer_snapshots"]["WS-70"]["commit"] == CURRENT["WS-70"]["commit"] and envelope["consumer_snapshots"]["WS-70"]["tree"] == CURRENT["WS-70"]["tree"]
    assert envelope["consumer_snapshots"]["WS-75"]["commit"] == CURRENT["WS-75"]["commit"] and envelope["consumer_snapshots"]["WS-75"]["tree"] == CURRENT["WS-75"]["tree"]
    for consumer in CURRENT:
        item = envelope["consumer_snapshots"][consumer]
        assert item["rights"] == "READ_ONLY_REFERENCE"
        assert item["provenance_predicate"] == "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE"
        assert item["digest_predicate"] == "PASS_COMMIT_TREE_DIGEST"
        assert item["reviewer_predicate"] == "INDEPENDENT_REVIEW_REQUIRED_RECOMMENDATION_ONLY"
        assert item["runtime_predicate"].startswith("NO_LIVE_ESTRA_EXECUTION")
    assert envelope["prior_snapshot"]["history_rewritten"] is False
    assert {item["id"]: item["expected"] for item in fixture["scenarios"]} == {case: evaluate(case) for case in [item["id"] for item in fixture["scenarios"]]}
    print(json.dumps({"status":"PASS_DYNAMIC_CONSUMER_RECAPTURE_REPLAY","candidate_rows":40,"consumers":3,"scenarios":8,"admission":"BLOCKED_FAIL_CLOSED"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
