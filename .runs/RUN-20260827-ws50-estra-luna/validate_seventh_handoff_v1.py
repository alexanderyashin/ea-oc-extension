from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENVELOPE = ROOT / "CANDIDATE_CONSUMER_HANDOFF_ENVELOPE_v1.json"
FIXTURE = ROOT / "SEVENTH_TRANCHE_HANDOFF_FIXTURE_v1.json"
REPORT = ROOT / "DOWNSTREAM_REVALIDATION_REPORT_v1.json"
FREEZE = ROOT / "CANDIDATE_FREEZE_MANIFEST_v1.json"

CAPTURED_REFS = {
    "WS-60-TOOLKIT": {"commit": "5196abf848d42b93ad120685f8bbe5006791c76b", "tree": "1c4850a72c12984cd6d6e5f25766533256f917f9"},
    "WS-75-PUBLICATION": {"commit": "2777fa80f821a0a91d6653df0951a5494f5f44d9", "tree": "e905599fb066c9bbb7b375b5ef767ab3761ec703"},
}


def main() -> None:
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert envelope["base_worker"] == {"commit": "9db64e071e346671bfa592043c87fd3207bfb0c7", "tree": "c1b77a2e05bcba158e6587f19713fe245df184db", "clean_at_capture": True}
    assert envelope["snapshot_timestamp_utc"].endswith("Z")
    assert envelope["snapshot_status"] == "STALE_AFTER_POST_CAPTURE_DRIFT__CAPTURE_PRESERVED"
    assert envelope["post_capture_readback"]["status"] == "STALE_SNAPSHOT"
    assert envelope["post_capture_readback"]["changed_consumers"] == ["WS-75-PUBLICATION"]
    assert envelope["post_capture_readback"]["captured_history_rewritten"] is False
    assert envelope["post_capture_readback"]["observed_refs"]["WS-75-PUBLICATION"] == {"commit":"4c3092f1eaee04b00b3a800864d1ecd31138a08e","tree":"fb0a96ce3a9387eb39827d70812dbb619be91d62"}
    assert envelope["claim_ceiling"] == "semantic-review-candidate-only"
    assert envelope["negative_boundaries"] == {"candidate_only": True, "no_promotion": True, "dominance": False, "holdout_delta": "NEGATIVE", "confidence_interval": "INCLUDES_ZERO", "feature_mutation": False, "source_mutation": False, "shared_logion_mutation": False, "empirical_execution": False, "publication_effect": False}
    assert len(envelope["candidate_rows"]) == 40
    expected = {row["path"]: row for row in report["candidate_rows"]}
    frozen = {row["path"]: row for row in freeze["files"]}
    actual = {row["path"]: row for row in envelope["candidate_rows"]}
    assert set(actual) == set(expected) == set(frozen)
    for path, row in actual.items():
        assert row["semantic_digest"] == frozen[path]["sha256"] == expected[path]["semantic_digest"]
        assert row["candidate_state"] == expected[path]["candidate_state"]
        assert row["rejection_profile"] == expected[path]["rejection_profile"]
    for consumer, captured in CAPTURED_REFS.items():
        assert envelope["consumer_refs"][consumer]["commit"] == captured["commit"]
        assert envelope["consumer_refs"][consumer]["tree"] == captured["tree"]
        assert envelope["consumer_refs"][consumer]["ref_mode"] == "READ_ONLY"
        assert envelope["consumer_refs"][consumer]["content_copied"] is False
    assert fixture["negative_boundaries"] == {"candidate_only": True, "no_promotion": True, "dominance": False, "holdout_delta": "NEGATIVE", "confidence_interval": "INCLUDES_ZERO", "source_mutation": False, "shared_logion_mutation": False}
    expected_scenarios = {
        "snapshot_current_at_capture": {"status":"PASS_READ_ONLY_HANDOFF","reason":"IMMUTABLE_CONSUMER_SNAPSHOT_CAPTURED"},
        "post_capture_consumer_drift": {"status":"STALE_SNAPSHOT","reason":"MARK_SNAPSHOT_STALE_NO_HISTORY_REWRITE"},
        "stale_consumer": {"status":"BLOCKED_CONSUMER_COMPATIBILITY","reason":"WS60_REJECT_STALE_CONSUMER_REF"},
        "provenance_mismatch": {"status":"BLOCKED_CONSUMER_COMPATIBILITY","reason":"WS60_REJECT_PROVENANCE_MISMATCH"},
        "private_runtime_path": {"status":"BLOCKED_CONSUMER_COMPATIBILITY","reason":"WS75_REJECT_PRIVATE_RUNTIME_PATH"},
        "widened_ceiling": {"status":"BLOCKED_CLAIM_CEILING","reason":"WS60_REJECT_WIDENED_CLAIM_CEILING"},
    }
    assert {item["id"]: item["expected"] for item in fixture["scenarios"]} == expected_scenarios
    print(json.dumps({"status":"PASS_SEVENTH_HANDOFF_ENVELOPE","candidate_rows":40,"captured_consumers":2,"scenarios":6,"snapshot_status":envelope["snapshot_status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
