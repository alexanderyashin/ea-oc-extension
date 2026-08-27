"""Pure completeness validator for the WS-50 A3 profile-review request manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RUN = Path(__file__).resolve().parent
MANIFEST_PATH = RUN / "A3_INDEPENDENT_PROFILE_REVIEW_REQUEST_MANIFEST_v1.json"

EXPECTED_CONSUMERS = ("WS-60", "WS-70", "WS-75")
EXPECTED_REFS = {
    "WS-60": {
        "role": "Toolkit",
        "repository": "estra-toolkit",
        "branch": "workstream/oc14-toolkit-luna-20260827",
        "commit": "c79ca249aa202718debacffe3b4a5566948a06ae",
        "tree": "a17246b0d1b6a4256e1c73c48170cdfab6fc2e24",
        "commit_tree_digest": "394ac0f7e84c3bb947d7b56cc050f8f1140ff972e4d43afefce4963d8482f509",
        "rights": "READ_ONLY_REFERENCE",
        "provenance": "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE",
        "runtime": "NO_LIVE_ESTRA_EXECUTION_NO_FEATURE_CATALOG_MUTATION",
    },
    "WS-70": {
        "role": "Machine/adapter downstream",
        "repository": "Logion",
        "branch": "workstream/oc14-machine-luna-20260827",
        "commit": "b0ba5b95a75cb507e08013aa6fb66df12e2e5b3d",
        "tree": "e65a8fcb2edad46bcf0c49d0b73586857ea74d3b",
        "commit_tree_digest": "acd39796340bf7d8009bf5a22a131a8280910e26ebf3f8b888544b3a592dba46",
        "rights": "READ_ONLY_REFERENCE",
        "provenance": "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE",
        "runtime": "NO_LIVE_ESTRA_EXECUTION_NO_FEATURE_CATALOG_MUTATION",
    },
    "WS-75": {
        "role": "Publication closeout",
        "repository": "Logion",
        "branch": "workstream/oc14-publication-luna-20260827",
        "commit": "160312105bf3e8448a958328152c123af0505443",
        "tree": "5045192778ef6dbe422d8a4b1e81ae72929cfd95",
        "commit_tree_digest": "f195080930cb12519802b32318db5a1fd76c08c99f190ca5155fd4a861e195be",
        "rights": "READ_ONLY_REFERENCE",
        "provenance": "PASS_EXACT_REPOSITORY_BRANCH_COMMIT_TREE",
        "runtime": "NO_LIVE_ESTRA_EXECUTION_NO_PUBLICATION_OR_DB_EFFECT",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    manifest_bytes = MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_bytes)
    require(
        manifest["schema_id"] == "ESTRA_WS50_A3_INDEPENDENT_PROFILE_REVIEW_REQUEST_MANIFEST_v1",
        "schema_id",
    )
    require(manifest["mode"] == "METADATA_ONLY_NO_SOURCE_CONTENT_MUTATION", "mode")
    require(manifest["base_worker"]["commit"] == "368ba5ecfc928f0a768d05cf7d3d7bfee454daf7", "base commit")
    require(manifest["base_worker"]["tree"] == "841685dfb9cdd3ec0b7ed4b1aba84a8838448464", "base tree")
    require(manifest["base_worker"]["clean_at_capture"] is True, "base clean")
    require(manifest["source_matrix"]["candidate_row_count"] == 40, "source row count")
    require(manifest["negative_boundaries"]["candidate_only"] is True, "candidate-only boundary")
    require(manifest["negative_boundaries"]["accepted"] == 0, "accepted boundary")
    require(manifest["negative_boundaries"]["dominance"] is False, "dominance boundary")
    require(manifest["negative_boundaries"]["holdout_delta"] == "NEGATIVE", "holdout boundary")
    require(manifest["negative_boundaries"]["confidence_interval"] == "INCLUDES_ZERO", "confidence boundary")
    require(manifest["negative_boundaries"]["promotion_forbidden"] is True, "promotion boundary")

    rows = manifest["rows"]
    require(len(rows) == 40, "rows must contain exactly 40 entries")
    seen = set()
    mapping_bound = applicability_bound = conformance_bound = holdout_bound = 0
    consumer_ref_sets = consumer_admission_receipts = consumer_reviewer_receipts = 0
    for expected_number, row in enumerate(rows, 1):
        path = row["path"]
        require(row["row_number"] == expected_number, f"row number {expected_number}")
        require(row["candidate_id"] == path and path not in seen, f"candidate id {path}")
        seen.add(path)
        mapping = row["oc_estra_mapping"]
        require(mapping["oc_math_producer_id"].startswith("WS-20-MATH@"), f"math mapping {path}")
        require(mapping["oc_metaontology_producer_id"].startswith("WS-30-METAONTOLOGY@"), f"meta mapping {path}")
        require(mapping["estra_concept"] and mapping["predicate"] and mapping["owner_route"], f"mapping fields {path}")
        require(mapping["review_receipt"] is None, f"mapping review must remain unresolved {path}")
        mapping_bound += 1

        applicability = row["applicability"]
        require(applicability["limit"] == "semantic-review-candidate-only", f"claim ceiling {path}")
        require(applicability["required_limit"] and applicability["owner_route"], f"applicability fields {path}")
        require(applicability["review_receipt"] is None, f"applicability review must remain unresolved {path}")
        applicability_bound += 1

        conformance = row["corpus_conformance"]
        require(conformance["semantic_digest"] and conformance["freeze_manifest"] == "CANDIDATE_FREEZE_MANIFEST_v1.json", f"corpus binding {path}")
        require(conformance["evidence_pointer"] and conformance["baseline_scope"] and conformance["owner_route"], f"conformance fields {path}")
        require(conformance["conformance_receipt"] is None, f"conformance review must remain unresolved {path}")
        conformance_bound += 1

        holdout = row["holdout_negative"]
        require(holdout["delta"] == "NEGATIVE" and holdout["confidence_interval"] == "INCLUDES_ZERO", f"holdout values {path}")
        require(holdout["dominance"] is False and holdout["promotion_forbidden"] is True, f"holdout flags {path}")
        require(holdout["evidence_pointer"] and holdout["owner_route"] and holdout["review_receipt"] is None, f"holdout fields {path}")
        holdout_bound += 1

        require(row["candidate_only"] is True and row["promotion_forbidden"] is True, f"row boundaries {path}")
        require(set(row["consumer_admission"]) == set(EXPECTED_CONSUMERS), f"consumer set {path}")
        for consumer in EXPECTED_CONSUMERS:
            actual = row["consumer_admission"][consumer]
            expected = EXPECTED_REFS[consumer]
            for key, value in expected.items():
                require(actual[key] == value, f"{consumer} {key} {path}")
            require(actual["admission_receipt"] is None, f"admission receipt must be null {consumer} {path}")
            require(actual["reviewer_receipt"] is None, f"reviewer receipt must be null {consumer} {path}")
            require(actual["owner_route"], f"owner route {consumer} {path}")
            consumer_ref_sets += 1

    counts = manifest["counts"]
    expected_counts = {
        "rows_total": 40,
        "mapping_bound": mapping_bound,
        "applicability_bound": applicability_bound,
        "corpus_conformance_bound": conformance_bound,
        "holdout_negative_bound": holdout_bound,
        "consumer_ref_sets_bound": consumer_ref_sets,
        "consumer_admission_receipts_present": consumer_admission_receipts,
        "consumer_reviewer_receipts_present": consumer_reviewer_receipts,
        "independent_engineering_review_receipts_present": 0,
        "complete_rows_for_acceptance": 0,
        "rows_returned_for_repair": 40,
    }
    require(counts == expected_counts, f"counts mismatch: {counts!r}")
    routes = manifest["missing_receipt_routes"]
    require(set(routes) == set((*EXPECTED_CONSUMERS, "independent_engineering_review")), "missing routes")
    require(manifest["request_contract"]["unresolved_receipts_must_be_null"] is True, "null receipt rule")
    require(manifest["request_contract"]["return_code"] == "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT", "return code")

    missing_slots = consumer_ref_sets * 2 + 1
    decision = "ACCEPT_PROFILE_REVIEW" if missing_slots == 0 else "RETURN_FOR_REPAIR_MISSING_CONSUMER_OR_INDEPENDENT_REVIEW_RECEIPT"
    result = {
        "validator": "validate_a3_profile_review_request_v1.py",
        "validator_status": "PASS_COMPLETE_MANIFEST",
        "accept_or_return": decision,
        "rows_total": len(rows),
        "rows_complete_for_request": len(rows),
        "rows_complete_for_acceptance": counts["complete_rows_for_acceptance"],
        "mapping_bound": mapping_bound,
        "applicability_bound": applicability_bound,
        "corpus_conformance_bound": conformance_bound,
        "holdout_negative_bound": holdout_bound,
        "consumer_ref_sets_bound": consumer_ref_sets,
        "missing_consumer_admission_receipts": consumer_ref_sets,
        "missing_consumer_reviewer_receipts": consumer_ref_sets,
        "missing_independent_engineering_review_receipts": 1,
        "missing_receipt_slots": missing_slots,
        "candidate_only": True,
        "accepted": 0,
        "dominance": False,
        "promotion_forbidden": True,
        "artifact_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "next_transition": "RETURN_FOR_REPAIR->CONSUMER_AND_INDEPENDENT_REVIEW_RECEIPTS",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
