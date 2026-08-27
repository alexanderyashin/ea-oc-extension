"""Pure validator/replay for the WS-50 A4 consumer-review watch packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
PACKET_PATH = RUN / "A4_CONSUMER_REVIEW_WATCH_REPAIR_PACKET_v1.json"
FIXTURE_PATH = RUN / "A4_CONSUMER_REVIEW_WATCH_REPLAY_FIXTURE_v1.json"
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


def replay(case_input: dict) -> str:
    if case_input.get("ref_state") == "STALE":
        return "BLOCKED_RECAPTURE_REQUIRED"
    if case_input.get("provenance") == "MISMATCH":
        return "BLOCKED_PROVENANCE"
    if case_input.get("digest") == "MISMATCH":
        return "BLOCKED_DIGEST"
    if case_input.get("rights") == "WRITE":
        return "BLOCKED_RIGHTS"
    if case_input.get("runtime") == "PRIVATE":
        return "BLOCKED_PRIVATE_RUNTIME"
    if case_input.get("claim_ceiling") == "WIDENED":
        return "BLOCKED_CLAIM_CEILING"
    if case_input.get("reviewer") == "AUTHORITY":
        return "BLOCKED_REVIEWER_AUTHORITY"
    retry = case_input.get("heartbeat_retry", 0)
    if retry == 3:
        return "ESCALATE_OWNER_REVIEWER"
    if retry in (1, 2):
        return f"HEARTBEAT_RETRY_{retry}"
    missing_admission = case_input.get("missing_admission", 0)
    missing_reviewer = case_input.get("missing_reviewer", 0)
    missing_independent = case_input.get("missing_independent", 0)
    if missing_independent:
        if missing_admission or missing_reviewer:
            return "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT"
        return "RETURN_FOR_REPAIR_MISSING_INDEPENDENT_REVIEW_RECEIPT"
    if missing_admission or missing_reviewer:
        return "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT"
    return "PROFILE_REVIEW_READY"


def main() -> None:
    packet_bytes = PACKET_PATH.read_bytes()
    packet = json.loads(packet_bytes)
    require(packet["schema_id"] == "ESTRA_WS50_A4_CONSUMER_REVIEW_WATCH_REPAIR_PACKET_v1", "schema")
    require(packet["mode"] == "PURE_METADATA_VALIDATOR_REPLAY_NEGATIVES_ONLY", "mode")
    require(packet["base_worker"]["commit"] == "368ba5ecfc928f0a768d05cf7d3d7bfee454daf7", "base commit")
    require(packet["base_worker"]["tree"] == "841685dfb9cdd3ec0b7ed4b1aba84a8838448464", "base tree")
    require(packet["base_worker"]["clean_at_capture"] is True, "base clean")
    require(packet["candidate_binding"] == {
        "manifest": "A3_INDEPENDENT_PROFILE_REVIEW_REQUEST_MANIFEST_v1.json",
        "rows": 40,
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "holdout_delta": "NEGATIVE",
        "confidence_interval": "INCLUDES_ZERO",
    }, "candidate binding")

    rows = packet["rows"]
    require(len(rows) == 40, "row count")
    seen = set()
    admission_missing = reviewer_missing = ref_sets = 0
    for number, row in enumerate(rows, 1):
        candidate_id = row["candidate_id"]
        require(row["row_number"] == number, f"row number {number}")
        require(candidate_id not in seen, f"duplicate candidate {candidate_id}")
        seen.add(candidate_id)
        require(row["row_candidate_only"] is True and row["row_promotion_forbidden"] is True, f"row boundary {candidate_id}")
        require(set(row["consumer_slots"]) == set(CONSUMERS), f"consumer set {candidate_id}")
        for consumer in CONSUMERS:
            slot = row["consumer_slots"][consumer]
            expected = EXPECTED[consumer]
            for key in ("repository", "branch", "commit", "tree", "commit_tree_digest"):
                require(slot["exact_ref"][key] == expected[key], f"{consumer} {key} {candidate_id}")
            require(slot["provenance_predicate"] == expected["provenance_predicate"], f"{consumer} provenance {candidate_id}")
            require(slot["rights_predicate"] == expected["rights_predicate"], f"{consumer} rights {candidate_id}")
            require(slot["runtime_predicate"] == expected["runtime_predicate"], f"{consumer} runtime {candidate_id}")
            require(slot["admission_receipt"] is None, f"admission must be null {consumer} {candidate_id}")
            require(slot["reviewer_receipt"] is None, f"reviewer must be null {consumer} {candidate_id}")
            require(slot["status"] == "MISSING" and slot["owner_route"], f"slot status/route {consumer} {candidate_id}")
            admission_missing += 1
            reviewer_missing += 1
            ref_sets += 1

    require(packet["slot_counts"] == {
        "candidate_rows": 40,
        "consumer_count": 3,
        "consumer_admission_slots": 120,
        "consumer_reviewer_slots": 120,
        "independent_engineering_review_slots": 1,
        "total_required_slots": 241,
        "admission_receipts_present": 0,
        "reviewer_receipts_present": 0,
        "independent_review_receipts_present": 0,
        "open_slots": 241,
    }, "slot counts")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    require(fixture["schema_id"] == "ESTRA_WS50_A4_CONSUMER_REVIEW_WATCH_REPLAY_FIXTURE_v1", "fixture schema")
    replay_pass = 0
    for case in fixture["cases"]:
        actual = replay(case["input"])
        require(actual == case["expected"], f"fixture {case['id']}: {actual} != {case['expected']}")
        replay_pass += 1

    result = {
        "validator": "validate_a4_consumer_review_watch_v1.py",
        "validator_status": "PASS_PURE_REPLAY_AND_COMPLETE_WATCH_PACKET",
        "watch_decision": "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT",
        "rows_total": len(rows),
        "consumer_ref_sets_bound": ref_sets,
        "missing_consumer_admission_receipts": admission_missing,
        "missing_consumer_reviewer_receipts": reviewer_missing,
        "missing_independent_engineering_review_receipts": 1,
        "open_slots": 241,
        "heartbeat_retries_max": 3,
        "replay_cases": len(fixture["cases"]),
        "replay_pass": replay_pass,
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "artifact_sha256": hashlib.sha256(packet_bytes).hexdigest(),
        "next_transition": "HEARTBEAT_RETRY_1_OR_ESCALATE_AFTER_RETRY_3_IDENTICAL",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
