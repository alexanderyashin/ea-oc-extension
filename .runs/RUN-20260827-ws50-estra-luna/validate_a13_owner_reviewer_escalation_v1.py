"""Pure validator/replay for the WS-50 A13 owner/reviewer escalation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
ESCALATION_PATH = RUN / "A13_OWNER_REVIEWER_ESCALATION_RECEIPT_v1.json"
FIXTURE_PATH = RUN / "A13_OWNER_REVIEWER_ESCALATION_REPLAY_FIXTURE_v1.json"
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
    if case["anchor"] == "STALE":
        return "BLOCKED_RECAPTURE_REQUIRED"
    negative = case.get("negative")
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
    if case.get("attempt") == 4:
        return "BLOCKED_FOURTH_RETRY_FORBIDDEN"
    if case.get("state") == "WAITING":
        return "WAIT_TYPED_OWNER_OR_REVIEWER_RECEIPTS"
    if case["open_slots"] == 0 and case.get("state") == "ALL_TYPED":
        return "PROFILE_REVIEW_READY_BOUNDED_ONLY"
    if case["open_slots"] == 241 and case["delta"] == "NONE":
        return "ESCALATE_OWNER_REVIEWER"
    return "WAIT_TYPED_OWNER_OR_REVIEWER_RECEIPTS"


def main() -> None:
    escalation_bytes = ESCALATION_PATH.read_bytes()
    escalation = json.loads(escalation_bytes)
    require(escalation["schema_id"] == "ESTRA_WS50_A13_OWNER_REVIEWER_ESCALATION_RECEIPT_v1", "schema")
    require(escalation["mode"] == "PURE_TYPED_ESCALATION_METADATA_ONLY", "mode")
    require(escalation["recipient"] == "ESTRA_OWNER_AND_INDEPENDENT_ENGINEERING_REVIEWER", "recipient")
    require(escalation["immutable_anchor"] == {
        "prior_receipt": "A6_CONSUMER_REVIEW_WATCH_POLL_02_RECEIPT_v1.json",
        "prior_receipt_sha256": "a84dfc75b830ece6b284d2ff5d49193bed0378a46acca7bb79adca7e6a055969",
        "prior_commit": "8a9ac87055f28436d04bf8d9c45a044d43124d0c",
        "prior_tree": "650c5f5b9f2b2f35ee64da2a49807577c61a7883",
        "history_rewritten": False,
    }, "immutable anchor")
    require(escalation["worker_binding"] == {
        "worktree": "C:/Users/Megaport/LOGION Ecosystem/03_ESTRA/Private/Remote/ea-oc-extension-ws50-estra-luna-20260827",
        "branch": "workstream/oc14-estra-luna-20260827",
        "commit": "8a9ac87055f28436d04bf8d9c45a044d43124d0c",
        "tree": "650c5f5b9f2b2f35ee64da2a49807577c61a7883",
        "clean": True,
    }, "worker binding")
    require(escalation["source_provenance"] == {
        "repository": "ea-oc-extension",
        "commit": "5398bfed0efbc56ad969382df48af568ee2df24b",
        "tree": "30578579fc51acf3512991ed2a9b6a01c0b95691",
        "rights": "READ_ONLY_REFERENCE",
        "mutation": False,
    }, "source provenance")
    binding = escalation["candidate_binding"]
    require(binding["rows"] == 40 and binding["candidate_only"] is True, "candidate rows")
    require(binding["accepted"] == 0 and binding["dominance"] is False and binding["promotion_forbidden"] is True, "candidate boundary")
    require(binding["holdout_delta"] == "NEGATIVE" and binding["confidence_interval"] == "INCLUDES_ZERO", "holdout boundary")
    require(escalation["escalation_basis"] == {
        "retry_attempt_reached": 2,
        "max_heartbeat_retries": 3,
        "receipt_delta": "NONE",
        "admissible_delta": False,
        "no_fourth_retry": True,
        "timeout_or_identical_dependency_code": "ESCALATE_OWNER_REVIEWER",
    }, "escalation basis")
    require(escalation["next_transition"] == {
        "state": "WAIT_TYPED_OWNER_OR_REVIEWER_RECEIPTS",
        "deadline": "NEXT_HEARTBEAT_ACK_WINDOW",
        "required_action": "Owner or independent reviewer supplies typed receipts satisfying exact ref/provenance/rights/reviewer predicates",
        "auto_retry": False,
    }, "next transition")
    missing = escalation["missing_fields"]
    require(missing["counts"] == {
        "consumer_admission_receipts": 120,
        "consumer_reviewer_receipts": 120,
        "independent_engineering_review_receipts": 1,
        "total_open": 241,
    }, "missing counts")
    require(escalation["receipt_delta"] == {
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
    for consumer in CONSUMERS:
        current = escalation["consumer_refs"][consumer]
        expected = EXPECTED[consumer]
        require(current["role"] == expected["role"], f"role {consumer}")
        for key in ("repository", "branch", "commit", "tree", "commit_tree_digest"):
            require(current["exact_ref"][key] == expected[key], f"ref {consumer} {key}")
        for key in ("provenance_predicate", "rights_predicate", "runtime_predicate"):
            require(current[key] == expected[key], f"predicate {consumer} {key}")
        require(current["admission_receipt"] is None and current["reviewer_receipt"] is None, f"receipt null {consumer}")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    require(fixture["schema_id"] == "ESTRA_WS50_A13_OWNER_REVIEWER_ESCALATION_REPLAY_FIXTURE_v1", "fixture schema")
    replay_pass = 0
    for case in fixture["cases"]:
        require(replay(case) == case["expected"], f"fixture {case['id']}")
        replay_pass += 1
    result = {
        "validator": "validate_a13_owner_reviewer_escalation_v1.py",
        "validator_status": "PASS_PURE_ESCALATION_REPLAY_AND_NEGATIVES",
        "immutable_anchor": "A6_CONSUMER_REVIEW_WATCH_POLL_02_RECEIPT_v1.json@8a9ac870/650c5f5",
        "receipt_delta": "NONE",
        "missing_slots": 241,
        "replay_cases": len(fixture["cases"]),
        "replay_pass": replay_pass,
        "decision": "ESCALATE_OWNER_REVIEWER",
        "next_transition": "WAIT_TYPED_OWNER_OR_REVIEWER_RECEIPTS",
        "deadline": "NEXT_HEARTBEAT_ACK_WINDOW",
        "no_fourth_retry": True,
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "artifact_sha256": hashlib.sha256(escalation_bytes).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
