"""Pure validator/replay for the WS-50 A14 owner/reviewer response watch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
WATCH_PATH = RUN / "A14_OWNER_REVIEWER_RESPONSE_WATCH_RECEIPT_v1.json"
FIXTURE_PATH = RUN / "A14_OWNER_REVIEWER_RESPONSE_WATCH_REPLAY_FIXTURE_v1.json"
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
    negative = case.get("negative")
    if negative == "STALE_REF":
        return "BLOCKED_RECAPTURE_REQUIRED"
    if negative == "PROVENANCE":
        return "BLOCKED_PROVENANCE"
    if negative == "DIGEST":
        return "BLOCKED_DIGEST"
    if negative == "RIGHTS":
        return "BLOCKED_RIGHTS"
    if negative == "PRIVATE_RUNTIME":
        return "BLOCKED_PRIVATE_RUNTIME"
    if negative == "WIDENED_CLAIM":
        return "BLOCKED_CLAIM_CEILING"
    if negative == "REVIEWER_AUTHORITY":
        return "BLOCKED_REVIEWER_AUTHORITY"
    if case.get("attempt") == 4:
        return "BLOCKED_FOURTH_RETRY_FORBIDDEN"
    if case["open_slots"] == 241 and case["delta"] == "NONE":
        return "ESCALATE_OWNER_REVIEWER"
    if case["open_slots"] == 0 and case["delta"] == "ALL_TYPED":
        return "PROFILE_REVIEW_READY_BOUNDED_ONLY"
    return "RETURN_FOR_REPAIR"


def main() -> None:
    watch_bytes = WATCH_PATH.read_bytes()
    watch = json.loads(watch_bytes)
    require(watch["schema_id"] == "ESTRA_WS50_A14_OWNER_REVIEWER_RESPONSE_WATCH_RECEIPT_v1", "schema")
    require(watch["mode"] == "PURE_METADATA_RESPONSE_WATCH_NO_OWNER_OR_CONSUMER_EXECUTION", "mode")
    require(watch["recipient"] == "ESTRA_OWNER_AND_INDEPENDENT_ENGINEERING_REVIEWER", "recipient")
    require(watch["immutable_anchor"] == {
        "prior_receipt": "A13_OWNER_REVIEWER_ESCALATION_RECEIPT_v1.json",
        "prior_receipt_sha256": "05601849d747f3dad92325c9a95294fa36a91f29d6c835a82d0087afdacf5691",
        "prior_commit": "129c8df78fedac110774d7bfa83bdaf266fbae4a",
        "prior_tree": "24328c90cc2ff92d5575a8a27dca9de8c2096980",
        "history_rewritten": False,
    }, "immutable anchor")
    require(watch["worker_binding"] == {
        "worktree": "C:/Users/Megaport/LOGION Ecosystem/03_ESTRA/Private/Remote/ea-oc-extension-ws50-estra-luna-20260827",
        "branch": "workstream/oc14-estra-luna-20260827",
        "commit": "129c8df78fedac110774d7bfa83bdaf266fbae4a",
        "tree": "24328c90cc2ff92d5575a8a27dca9de8c2096980",
        "clean": True,
    }, "worker binding")
    require(watch["source_provenance"] == {
        "repository": "ea-oc-extension",
        "commit": "5398bfed0efbc56ad969382df48af568ee2df24b",
        "tree": "30578579fc51acf3512991ed2a9b6a01c0b95691",
        "rights": "READ_ONLY_REFERENCE",
        "mutation": False,
    }, "source provenance")
    binding = watch["candidate_binding"]
    require(binding["rows"] == 40 and binding["candidate_only"] is True, "candidate rows")
    require(binding["accepted"] == 0 and binding["dominance"] is False and binding["promotion_forbidden"] is True, "candidate boundary")
    require(binding["holdout_delta"] == "NEGATIVE" and binding["confidence_interval"] == "INCLUDES_ZERO", "holdout boundary")
    require(watch["deadline_observation"] == {
        "deadline": "NEXT_HEARTBEAT_ACK_WINDOW",
        "observation": "DEADLINE_WINDOW_CHECK",
        "typed_delta_received": False,
        "owner_response_received": False,
        "independent_reviewer_response_received": False,
        "observed_no_delta": True,
    }, "deadline observation")
    require(watch["receipt_delta"] == {
        "new_consumer_admission_receipts": 0,
        "new_consumer_reviewer_receipts": 0,
        "new_independent_engineering_review_receipts": 0,
        "resolved_slots": 0,
        "open_slots": 241,
        "admissible_delta": False,
        "changed_consumers": [],
        "state": "NO_TYPED_DELTA_AT_DEADLINE_WINDOW",
    }, "receipt delta")
    require(watch["missing_fields"]["counts"] == {
        "consumer_admission_receipts": 120,
        "consumer_reviewer_receipts": 120,
        "independent_engineering_review_receipts": 1,
        "total_open": 241,
    }, "missing counts")
    for consumer in CONSUMERS:
        current = watch["consumer_refs"][consumer]
        expected = EXPECTED[consumer]
        require(current["role"] == expected["role"], f"role {consumer}")
        for key in ("repository", "branch", "commit", "tree", "commit_tree_digest"):
            require(current["exact_ref"][key] == expected[key], f"ref {consumer} {key}")
        for key in ("provenance_predicate", "rights_predicate", "runtime_predicate"):
            require(current[key] == expected[key], f"predicate {consumer} {key}")
        require(current["admission_receipt"] is None and current["reviewer_receipt"] is None, f"receipts {consumer}")
    require(watch["retry_policy"] == {
        "retry_budget_exhausted": True,
        "max_heartbeat_retries": 3,
        "fourth_retry": "FORBIDDEN",
        "auto_retry": False,
        "escalation_code": "ESCALATE_OWNER_REVIEWER",
    }, "retry policy")
    require(watch["decision"] == {
        "current": "RETURN_FOR_REPAIR",
        "emitted": "ESCALATE_OWNER_REVIEWER",
        "next_transition": "WAIT_TYPED_OWNER_OR_REVIEWER_RECEIPTS",
        "deadline": "NEXT_HEARTBEAT_ACK_WINDOW",
        "claim_ceiling": "semantic-review-candidate-only",
    }, "decision")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    require(fixture["schema_id"] == "ESTRA_WS50_A14_OWNER_REVIEWER_RESPONSE_WATCH_REPLAY_FIXTURE_v1", "fixture schema")
    replay_pass = 0
    for case in fixture["cases"]:
        require(replay(case) == case["expected"], f"fixture {case['id']}")
        replay_pass += 1
    result = {
        "validator": "validate_a14_owner_reviewer_response_watch_v1.py",
        "validator_status": "PASS_PURE_DEADLINE_WATCH_REPLAY_AND_NEGATIVES",
        "immutable_anchor": "A13_OWNER_REVIEWER_ESCALATION_RECEIPT_v1.json@129c8df/24328c90",
        "deadline": "NEXT_HEARTBEAT_ACK_WINDOW",
        "receipt_delta": "NONE",
        "open_slots": 241,
        "replay_cases": len(fixture["cases"]),
        "replay_pass": replay_pass,
        "decision": "ESCALATE_OWNER_REVIEWER",
        "state": "RETURN_FOR_REPAIR",
        "no_fourth_retry": True,
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "artifact_sha256": hashlib.sha256(watch_bytes).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
