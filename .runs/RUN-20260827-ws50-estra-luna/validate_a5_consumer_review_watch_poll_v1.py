"""Pure validator/replay for the WS-50 A5 bounded consumer-review poll."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
POLL_PATH = RUN / "A5_CONSUMER_REVIEW_WATCH_POLL_01_RECEIPT_v1.json"
FIXTURE_PATH = RUN / "A5_CONSUMER_REVIEW_WATCH_POLL_01_REPLAY_FIXTURE_v1.json"
CONSUMERS = ("WS-60", "WS-70", "WS-75")
EXPECTED = {
    "WS-60": {
        "role": "Toolkit",
        "repository": "estra-toolkit",
        "branch": "workstream/oc14-toolkit-luna-20260827",
        "commit": "c79ca249aa202718debacffe3b4a5566948a06ae",
        "tree": "a17246b0d1b6a4256e1c73c48170cdfab6fc2e24",
        "commit_tree_digest": "394ac0f7e84c3bb947d7b56cc050f8f1140ff972e4d43afefce4963d8482f509",
        "provenance_predicate": "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE",
        "rights_predicate": "READ_ONLY_REFERENCE",
        "runtime_predicate": "NO_LIVE_ESTRA_EXECUTION_NO_FEATURE_CATALOG_MUTATION",
    },
    "WS-70": {
        "role": "Machine/adapter downstream",
        "repository": "Logion",
        "branch": "workstream/oc14-machine-luna-20260827",
        "commit": "b0ba5b95a75cb507e08013aa6fb66df12e2e5b3d",
        "tree": "e65a8fcb2edad46bcf0c49d0b73586857ea74d3b",
        "commit_tree_digest": "acd39796340bf7d8009bf5a22a131a8280910e26ebf3f8b888544b3a592dba46",
        "provenance_predicate": "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE",
        "rights_predicate": "READ_ONLY_REFERENCE",
        "runtime_predicate": "NO_LIVE_ESTRA_EXECUTION_NO_FEATURE_CATALOG_MUTATION",
    },
    "WS-75": {
        "role": "Publication closeout",
        "repository": "Logion",
        "branch": "workstream/oc14-publication-luna-20260827",
        "commit": "160312105bf3e8448a958328152c123af0505443",
        "tree": "5045192778ef6dbe422d8a4b1e81ae72929cfd95",
        "commit_tree_digest": "f195080930cb12519802b32318db5a1fd76c08c99f190ca5155fd4a861e195be",
        "provenance_predicate": "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE",
        "rights_predicate": "READ_ONLY_REFERENCE",
        "runtime_predicate": "NO_LIVE_ESTRA_EXECUTION_NO_PUBLICATION_OR_DB_EFFECT",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def replay(case: dict) -> str:
    state = case["state"]
    if state == "STALE_REF":
        return "BLOCKED_RECAPTURE_REQUIRED"
    if state == "PROVENANCE_MISMATCH":
        return "BLOCKED_PROVENANCE"
    if state == "DIGEST_MISMATCH":
        return "BLOCKED_DIGEST"
    if state == "RIGHTS_MISMATCH":
        return "BLOCKED_RIGHTS"
    if state == "PRIVATE_RUNTIME":
        return "BLOCKED_PRIVATE_RUNTIME"
    if state == "WIDENED_CLAIM":
        return "BLOCKED_CLAIM_CEILING"
    if state == "REVIEWER_AUTHORITY":
        return "BLOCKED_REVIEWER_AUTHORITY"
    if case["attempt"] == 3 and state in {"IDENTICAL", "TIMEOUT"}:
        return "ESCALATE_OWNER_REVIEWER"
    if state == "IDENTICAL" and case["attempt"] in {1, 2}:
        return f"HEARTBEAT_RETRY_{case['attempt']}"
    if state == "RECEIPTS_PARTIAL":
        return "RETURN_FOR_REPAIR_MISSING_INDEPENDENT_REVIEW_RECEIPT"
    if state == "ALL_RECEIPTS_PRESENT" and case["open_slots"] == 0:
        return "PROFILE_REVIEW_READY"
    return "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT"


def main() -> None:
    poll_bytes = POLL_PATH.read_bytes()
    poll = json.loads(poll_bytes)
    require(poll["schema_id"] == "ESTRA_WS50_A5_CONSUMER_REVIEW_WATCH_POLL_RECEIPT_v1", "schema")
    require(poll["mode"] == "PURE_METADATA_POLL_NO_CONSUMER_EXECUTION", "mode")
    require(poll["poll_attempt"] == 1 and poll["max_heartbeat_retries"] == 3, "poll bounds")
    require(poll["worker_binding"] == {
        "worktree": "C:/Users/Megaport/LOGION Ecosystem/03_ESTRA/Private/Remote/ea-oc-extension-ws50-estra-luna-20260827",
        "branch": "workstream/oc14-estra-luna-20260827",
        "commit": "ed945a3bf535858be963cb4a063022027ea1fb7b",
        "tree": "42b281278fec32b490f165ce609661b11eddd832",
        "clean": True,
    }, "worker binding")
    require(poll["source_provenance"] == {
        "repository": "ea-oc-extension",
        "commit": "5398bfed0efbc56ad969382df48af568ee2df24b",
        "tree": "30578579fc51acf3512991ed2a9b6a01c0b95691",
        "rights": "READ_ONLY_REFERENCE",
        "mutation": False,
    }, "source provenance")
    binding = poll["candidate_binding"]
    require(binding["rows"] == 40 and binding["candidate_only"] is True, "candidate rows")
    require(binding["accepted"] == 0 and binding["dominance"] is False and binding["promotion_forbidden"] is True, "candidate boundary")
    require(binding["holdout_delta"] == "NEGATIVE" and binding["confidence_interval"] == "INCLUDES_ZERO", "holdout boundary")
    observed = poll["observed_slots"]
    require(observed == {
        "candidate_rows": 40,
        "consumer_admission_missing": 120,
        "consumer_reviewer_missing": 120,
        "independent_engineering_review_missing": 1,
        "total_open": 241,
        "state_is_identical_to_previous_poll": True,
    }, "observed slots")
    for consumer in CONSUMERS:
        current = poll["consumer_refs"][consumer]
        expected = EXPECTED[consumer]
        require(current["role"] == expected["role"], f"role {consumer}")
        for key in ("repository", "branch", "commit", "tree", "commit_tree_digest"):
            require(current["exact_ref"][key] == expected[key], f"ref {consumer} {key}")
        for key in ("provenance_predicate", "rights_predicate", "runtime_predicate"):
            require(current[key] == expected[key], f"predicate {consumer} {key}")
        require(current["admission_receipt"] is None and current["reviewer_receipt"] is None, f"missing receipts {consumer}")
        require(current["admission_missing_rows"] == 40 and current["reviewer_missing_rows"] == 40, f"counts {consumer}")
    independent = poll["independent_engineering_review"]
    require(independent["receipt"] is None and independent["status"] == "MISSING", "independent review")
    require(poll["decision"] == {
        "current": "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT",
        "next_transition": "HEARTBEAT_RETRY_2",
        "escalation_code": "ESCALATE_OWNER_REVIEWER",
    }, "decision")
    require(poll["timeout_policy"]["after_attempt_3"] == "ESCALATE_OWNER_REVIEWER", "timeout escalation")
    require(poll["timeout_policy"]["auto_retry_after_escalation"] is False, "escalation retry")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    require(fixture["schema_id"] == "ESTRA_WS50_A5_CONSUMER_REVIEW_WATCH_POLL_REPLAY_FIXTURE_v1", "fixture schema")
    replay_pass = 0
    for case in fixture["cases"]:
        require(replay(case) == case["expected"], f"fixture {case['id']}")
        replay_pass += 1
    result = {
        "validator": "validate_a5_consumer_review_watch_poll_v1.py",
        "validator_status": "PASS_PURE_POLL_REPLAY_AND_NEGATIVES",
        "poll_attempt": 1,
        "max_heartbeat_retries": 3,
        "rows_total": 40,
        "open_slots": 241,
        "consumer_admission_missing": 120,
        "consumer_reviewer_missing": 120,
        "independent_review_missing": 1,
        "replay_cases": len(fixture["cases"]),
        "replay_pass": replay_pass,
        "decision": "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT",
        "next_transition": "HEARTBEAT_RETRY_2",
        "timeout_transition": "ESCALATE_OWNER_REVIEWER",
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "artifact_sha256": hashlib.sha256(poll_bytes).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
