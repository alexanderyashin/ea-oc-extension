"""Pure validator/replay for the WS-50 A6 bounded consumer-review poll."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
POLL_PATH = RUN / "A6_CONSUMER_REVIEW_WATCH_POLL_02_RECEIPT_v1.json"
FIXTURE_PATH = RUN / "A6_CONSUMER_REVIEW_WATCH_POLL_02_REPLAY_FIXTURE_v1.json"
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
    if case["attempt"] >= 2 and case["delta"] == "NONE" and case["open_slots"] == 241:
        return "ESCALATE_OWNER_REVIEWER"
    if state == "RECEIPTS_PARTIAL" and case["open_slots"] == 1:
        return "RETURN_FOR_REPAIR_MISSING_INDEPENDENT_REVIEW_RECEIPT"
    if state == "ALL_RECEIPTS_PRESENT" and case["open_slots"] == 0:
        return "PROFILE_REVIEW_READY"
    return "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT"


def main() -> None:
    poll_bytes = POLL_PATH.read_bytes()
    poll = json.loads(poll_bytes)
    require(poll["schema_id"] == "ESTRA_WS50_A6_CONSUMER_REVIEW_WATCH_POLL_02_RECEIPT_v1", "schema")
    require(poll["mode"] == "PURE_METADATA_HEARTBEAT_NO_CONSUMER_EXECUTION", "mode")
    require(poll["poll_attempt"] == 2 and poll["max_heartbeat_retries"] == 3, "poll bounds")
    require(poll["immutable_anchor"] == {
        "prior_receipt": "A5_CONSUMER_REVIEW_WATCH_POLL_01_RECEIPT_v1.json",
        "prior_commit": "bcbe477385b5266aa71380b5fdeafc4e5fd5e689",
        "prior_tree": "7a17fb5cef4044b3e169360ce65a14200f40768f",
        "prior_receipt_sha256": "3b56f425eb0d944789810a3572483fded121c70e7d4ffada3f27f63ddefe1091",
        "history_rewritten": False,
    }, "immutable anchor")
    require(poll["worker_binding"] == {
        "worktree": "C:/Users/Megaport/LOGION Ecosystem/03_ESTRA/Private/Remote/ea-oc-extension-ws50-estra-luna-20260827",
        "branch": "workstream/oc14-estra-luna-20260827",
        "commit": "bcbe477385b5266aa71380b5fdeafc4e5fd5e689",
        "tree": "7a17fb5cef4044b3e169360ce65a14200f40768f",
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
    require(poll["receipt_delta"] == {
        "new_admission_receipts": 0,
        "new_reviewer_receipts": 0,
        "new_independent_review_receipts": 0,
        "resolved_slots": 0,
        "opened_slots": 0,
        "unchanged_slots": 241,
        "admissible_delta": False,
        "changed_consumers": [],
        "state": "NO_ADMISSIBLE_DELTA_RETRY_2",
    }, "receipt delta")
    require(poll["observed_slots"] == {
        "candidate_rows": 40,
        "consumer_admission_missing": 120,
        "consumer_reviewer_missing": 120,
        "independent_engineering_review_missing": 1,
        "total_open": 241,
        "delta_from_poll_1": "NONE",
    }, "observed slots")
    missing = poll["missing_fields"]
    require(missing["counts"] == {
        "consumer_admission_receipts": 120,
        "consumer_reviewer_receipts": 120,
        "independent_engineering_review_receipts": 1,
        "total": 241,
    }, "missing counts")
    require(missing["consumer_admission_receipt"] == [
        "rows[1..40].consumer_slots.WS-60.admission_receipt",
        "rows[1..40].consumer_slots.WS-70.admission_receipt",
        "rows[1..40].consumer_slots.WS-75.admission_receipt",
    ], "admission missing fields")
    require(missing["consumer_reviewer_receipt"] == [
        "rows[1..40].consumer_slots.WS-60.reviewer_receipt",
        "rows[1..40].consumer_slots.WS-70.reviewer_receipt",
        "rows[1..40].consumer_slots.WS-75.reviewer_receipt",
    ], "reviewer missing fields")
    require(missing["independent_engineering_review_receipt"] == ["independent_engineering_review.receipt"], "independent missing field")
    for consumer in CONSUMERS:
        current = poll["consumer_refs"][consumer]
        expected = EXPECTED[consumer]
        require(current["role"] == expected["role"], f"role {consumer}")
        for key in ("repository", "branch", "commit", "tree", "commit_tree_digest"):
            require(current["exact_ref"][key] == expected[key], f"ref {consumer} {key}")
        for key in ("provenance_predicate", "rights_predicate", "runtime_predicate"):
            require(current[key] == expected[key], f"predicate {consumer} {key}")
        require(current["admission_receipt"] is None and current["reviewer_receipt"] is None, f"receipts {consumer}")
        require(current["admission_missing_rows"] == 40 and current["reviewer_missing_rows"] == 40, f"counts {consumer}")
    require(poll["retry_policy"]["current_retry"] == 2, "current retry")
    require(poll["retry_policy"]["no_admissible_delta_at_retry_2"] is True, "no delta flag")
    require(poll["retry_policy"]["escalation"] == {
        "status": "ESCALATE_OWNER",
        "code": "ESCALATE_OWNER_REVIEWER",
        "route": "OC14 router + WS-50 owner + WS-60/70/75 consumer/reviewer owners",
        "auto_retry": False,
    }, "escalation")
    require(poll["decision"] == {
        "current": "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT",
        "emitted": "ESCALATE_OWNER_REVIEWER",
        "next_transition": "OWNER_REVIEWER_ACTION_REQUIRED",
        "claim_ceiling": "semantic-review-candidate-only",
    }, "decision")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    require(fixture["schema_id"] == "ESTRA_WS50_A6_CONSUMER_REVIEW_WATCH_POLL_02_REPLAY_FIXTURE_v1", "fixture schema")
    replay_pass = 0
    for case in fixture["cases"]:
        require(replay(case) == case["expected"], f"fixture {case['id']}")
        replay_pass += 1
    result = {
        "validator": "validate_a6_consumer_review_watch_poll_v1.py",
        "validator_status": "PASS_PURE_RETRY_2_REPLAY_AND_NEGATIVES",
        "poll_attempt": 2,
        "max_heartbeat_retries": 3,
        "rows_total": 40,
        "open_slots": 241,
        "receipt_delta": "NONE",
        "missing_consumer_admission_receipts": 120,
        "missing_consumer_reviewer_receipts": 120,
        "missing_independent_engineering_review_receipts": 1,
        "replay_cases": len(fixture["cases"]),
        "replay_pass": replay_pass,
        "decision": "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT",
        "emitted": "ESCALATE_OWNER_REVIEWER",
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "artifact_sha256": hashlib.sha256(poll_bytes).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
