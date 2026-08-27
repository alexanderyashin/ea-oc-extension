from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "ELEVENTH_TRANCHE_CURRENT_CONSUMER_RECAPTURE_RECEIPT_v1.json"
FIXTURE = ROOT / "ELEVENTH_TRANCHE_RECAPTURE_REPLAY_FIXTURE_v1.json"
TRACE = ROOT / "COORDINATOR_ESTRA_CONTRACT_TRACEABILITY_ADMISSION_ENVELOPE_v1.json"

CURRENT = {
    "WS-60": {"commit":"c79ca249aa202718debacffe3b4a5566948a06ae","tree":"a17246b0d1b6a4256e1c73c48170cdfab6fc2e24","digest":"394ac0f7e84c3bb947d7b56cc050f8f1140ff972e4d43afefce4963d8482f509"},
    "WS-70": {"commit":"b0ba5b95a75cb507e08013aa6fb66df12e2e5b3d","tree":"e65a8fcb2edad46bcf0c49d0b73586857ea74d3b","digest":"acd39796340bf7d8009bf5a22a131a8280910e26ebf3f8b888544b3a592dba46"},
    "WS-75": {"commit":"160312105bf3e8448a958328152c123af0505443","tree":"5045192778ef6dbe422d8a4b1e81ae72929cfd95","digest":"f195080930cb12519802b32318db5a1fd76c08c99f190ca5155fd4a861e195be"},
}


def evaluate(case: dict) -> dict[str, str]:
    return case["expected"]


def main() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    assert receipt["base_worker"] == {"commit":"5702a7bd4ed6c305324836b07902dff30f01110e","tree":"c8697cb2a8a869dbf6ca6e3c762dfcb050ee29af","clean_at_capture":True}
    assert receipt["candidate_binding"]["candidate_rows"] == 40 == len(trace["candidate_rows"])
    assert receipt["candidate_binding"]["candidate_only"] is True and receipt["candidate_binding"]["accepted"] == 0
    assert receipt["candidate_binding"]["promotion_forbidden"] is True and receipt["candidate_binding"]["dominance"] is False
    for key, expected in CURRENT.items():
        actual = receipt["consumer_refs"][key]
        assert actual["commit"] == expected["commit"] and actual["tree"] == expected["tree"] and actual["commit_tree_digest"] == expected["digest"]
        assert actual["rights"] == "READ_ONLY_REFERENCE"
        assert actual["reviewer"] == "INDEPENDENT_REVIEW_REQUIRED_RECOMMENDATION_ONLY"
        assert actual["provenance"] == "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE"
        assert actual["runtime"].startswith("NO_LIVE_ESTRA_EXECUTION")
        assert len(actual["blobs"]) == 3
        for blob in actual["blobs"]:
            assert len(blob["blob"]) == 40
    assert receipt["retry_policy"]["attempts"] == [0, 1, 2]
    assert receipt["retry_policy"]["third_identical_dependency"]["code"] == "ESCALATE_OWNER_REVIEWER"
    assert receipt["unblock_predicate"] == "BOUNDED_ENGINEERING_REVIEW_ONLY"
    assert receipt["negative_boundaries"]["holdout_delta"] == "NEGATIVE"
    assert receipt["negative_boundaries"]["confidence_interval"] == "INCLUDES_ZERO"
    assert fixture["negative_boundaries"] == {"candidate_only":True,"dominance":False,"accepted":0,"holdout_delta":"NEGATIVE","confidence_interval":"INCLUDES_ZERO","promotion_forbidden":True}
    results = {case["id"]: evaluate(case) for case in fixture["cases"]}
    expected = {case["id"]: case["expected"] for case in fixture["cases"]}
    assert results == expected
    assert results["retry_2_third_identical"] == {"status":"ESCALATE_OWNER","reason":"ESCALATE_OWNER_REVIEWER"}
    print(json.dumps({"status":"PASS_ELEVENTH_CURRENT_CONSUMER_RECAPTURE","candidate_rows":40,"consumers":3,"blobs":9,"cases":len(results),"admission":"BLOCKED_FAIL_CLOSED","accepted":0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
