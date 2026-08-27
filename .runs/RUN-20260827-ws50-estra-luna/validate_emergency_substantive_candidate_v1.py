"""Pure validator/replay for the emergency WS-50 candidate packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
PACKET_PATH = RUN / "EMERGENCY_SUBSTANTIVE_CANDIDATE_GENERATION_PACKET_v1.json"
FIXTURE_PATH = RUN / "EMERGENCY_SUBSTANTIVE_CANDIDATE_REPLAY_FIXTURE_v1.json"
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
    if negative == "RIGHTS":
        return "BLOCKED_RIGHTS"
    if negative == "PRIVATE_RUNTIME":
        return "BLOCKED_PRIVATE_RUNTIME"
    if negative == "WIDENED_CLAIM":
        return "BLOCKED_CLAIM_CEILING"
    if negative == "SOURCE_MUTATION":
        return "BLOCKED_SOURCE_MUTATION"
    if negative == "AUTHORITY":
        return "BLOCKED_AUTHORITY"
    if case.get("missing") == "mapping":
        return "BLOCKED_INCOMPLETE_MAPPING"
    if case.get("missing") == "applicability_ceiling":
        return "BLOCKED_CLAIM_CEILING"
    if case.get("holdout") == "POSITIVE":
        return "BLOCKED_DOMINANCE_BOUNDARY"
    if case.get("open_slots", 0) > 0:
        return "BLOCKED_DEPENDENCY_RECEIPTS_OPEN"
    return "PASS_CANDIDATE_PACKET"


def main() -> None:
    packet_bytes = PACKET_PATH.read_bytes()
    packet = json.loads(packet_bytes)
    require(packet["schema_id"] == "ESTRA_WS50_EMERGENCY_SUBSTANTIVE_CANDIDATE_GENERATION_PACKET_v1", "schema")
    require(packet["mode"] == "BOUNDED_FRAMEWORK_ENGINEERING_CANDIDATE_NO_SOURCE_MUTATION", "mode")
    require(packet["base_worker"] == {
        "worktree": "C:/Users/Megaport/LOGION Ecosystem/03_ESTRA/Private/Remote/ea-oc-extension-ws50-estra-luna-20260827",
        "branch": "workstream/oc14-estra-luna-20260827",
        "commit": "a13e7541e9bb253e0ede17be097ef612a7b28f25",
        "tree": "2629f971e0a6af486b85a729096b4bddca262033",
        "clean_at_capture": True,
    }, "base worker")
    require(packet["source_provenance"] == {
        "repository": "ea-oc-extension",
        "commit": "5398bfed0efbc56ad969382df48af568ee2df24b",
        "tree": "30578579fc51acf3512991ed2a9b6a01c0b95691",
        "rights": "READ_ONLY_REFERENCE",
        "mutation": False,
    }, "source provenance")
    binding = packet["candidate_binding"]
    require(binding["rows"] == 40 and binding["candidate_only"] is True, "candidate binding")
    require(binding["accepted"] == 0 and binding["dominance"] is False and binding["promotion_forbidden"] is True, "candidate boundary")
    require(binding["holdout_delta"] == "NEGATIVE" and binding["confidence_interval"] == "INCLUDES_ZERO", "holdout boundary")
    require(packet["interface_contract_map"]["adapter_rule"].startswith("Candidate adapters expose descriptor-level"), "adapter rule")

    rows = packet["rows"]
    require(len(rows) == 40, "row count")
    seen = set()
    for number, row in enumerate(rows, 1):
        require(row["row_number"] == number, f"row number {number}")
        require(row["candidate_id"] == row["path"] and row["candidate_id"] not in seen, f"candidate id {number}")
        seen.add(row["candidate_id"])
        require(row["producer_bindings"]["oc_math_producer_id"].startswith("WS-20-MATH@"), f"math producer {number}")
        require(row["producer_bindings"]["oc_metaontology_producer_id"].startswith("WS-30-METAONTOLOGY@"), f"meta producer {number}")
        require(row["estra_concept"] and row["applicability_limit"], f"mapping/applicability {number}")
        require(row["corpus_conformance_evidence"]["semantic_digest"], f"digest {number}")
        holdout = row["holdout_status"]
        require(holdout["delta"] == "NEGATIVE" and holdout["confidence_interval"] == "INCLUDES_ZERO" and holdout["dominance"] is False, f"holdout {number}")
        require(row["interface_contract"]["candidate_implementation"] == "DESCRIPTOR_ONLY_NO_SOURCE_IMPLEMENTATION", f"implementation boundary {number}")
        require(row["candidate_only"] is True and row["promotion_forbidden"] is True, f"row boundary {number}")

    slots = packet["open_receipt_slots"]
    require(len(slots) == 241, "slot total")
    require(len({slot["slot_id"] for slot in slots}) == 241, "slot uniqueness")
    require(sum(slot["kind"] == "admission_receipt" for slot in slots) == 120, "admission slots")
    require(sum(slot["kind"] == "reviewer_receipt" for slot in slots) == 120, "reviewer slots")
    require(sum(slot["kind"] == "independent_engineering_review_receipt" for slot in slots) == 1, "independent slot")
    require(all(slot["receipt"] is None and slot["status"] == "OPEN_MISSING" and slot["owner_route"] for slot in slots), "open slot state")
    require(packet["consumer_handoff"]["open_slot_total"] == 241, "handoff slot count")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    require(fixture["schema_id"] == "ESTRA_WS50_EMERGENCY_SUBSTANTIVE_CANDIDATE_REPLAY_FIXTURE_v1", "fixture schema")
    replay_pass = 0
    for case in fixture["cases"]:
        require(replay(case) == case["expected"], f"fixture {case['id']}")
        replay_pass += 1
    result = {
        "validator": "validate_emergency_substantive_candidate_v1.py",
        "validator_status": "PASS_PURE_CANDIDATE_REPLAY_AND_NEGATIVES",
        "rows_total": len(rows),
        "interface_contract_rows": len(rows),
        "open_receipt_slots": len(slots),
        "consumer_admission_slots": 120,
        "consumer_reviewer_slots": 120,
        "independent_review_slots": 1,
        "replay_cases": len(fixture["cases"]),
        "replay_pass": replay_pass,
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "consumer_handoff": "DESCRIPTOR_ONLY_RECEIPT_GATED",
        "artifact_sha256": hashlib.sha256(packet_bytes).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
