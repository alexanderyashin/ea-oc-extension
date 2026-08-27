from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "DEPENDENCY_GATE_FIXTURE_v1.json"
MATRIX = ROOT / "CANDIDATE_TO_CLAIM_MATRIX_v1.json"
FREEZE = ROOT / "CANDIDATE_FREEZE_MANIFEST_v1.json"


def result(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def evaluate(scenario: dict, fixture: dict) -> dict[str, str]:
    accepted = fixture["accepted_producers"]
    roles = {receipt["role"]: receipt for receipt in scenario["receipts"]}
    if set(roles) != set(fixture["gate_contract"]["required_roles"]):
        return result("BLOCKED_DEPENDENCY", "REJECT_UNACCEPTED_PRODUCER")

    for role, receipt in roles.items():
        expected = accepted[role]
        required = fixture["gate_contract"]["required_receipt_fields"]
        if any(field not in receipt for field in required):
            return result("BLOCKED_DEPENDENCY", "REJECT_UNACCEPTED_PRODUCER")
        if any(receipt[field] != expected[field] for field in required):
            return result("BLOCKED_DEPENDENCY", "REJECT_UNACCEPTED_PRODUCER")

    context = scenario.get("claim_context", {})
    if "OC14-OB-MATH-03" in context.get("open_obligations", []):
        return result("BLOCKED_DEPENDENCY", "REJECT_UNACCEPTED_PRODUCER")
    if any(receipt.get("dependency_state") == "MATH-03 OPEN" for receipt in roles.values()):
        return result("BLOCKED_DEPENDENCY", "REJECT_UNACCEPTED_PRODUCER")
    if context.get("holdout_delta") == "NEGATIVE" and context.get("confidence_interval") == "INCLUDES_ZERO":
        return result("BLOCKED_CLAIM_CEILING", "REJECT_NEGATIVE_HOLDOUT")
    if context.get("requested_claim") == "typed-history-dominance":
        return result("BLOCKED_CLAIM_CEILING", "REJECT_WIDENED_CLAIM_CEILING")
    return result("PASS_DEPENDENCY_GATE_REVIEW_ONLY", "ACCEPT_EXACT_PRODUCER_RECEIPTS")


def main() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    expectations = fixture["candidate_expectations"]
    matrix_rows = matrix["rows"]
    assert len(expectations) == 40 == matrix["row_count"] == len(matrix_rows)
    assert {row["path"] for row in expectations} == {row["path"] for row in matrix_rows}
    assert {row["path"] for row in expectations} == {row["path"] for row in freeze["files"]}
    for expectation in expectations:
        matching = next(row for row in matrix_rows if row["path"] == expectation["path"])
        assert expectation["matrix_status"] == matching["semantic_status"]
        assert expectation["downstream_consumers"] == matching["downstream_consumer"]
        assert expectation["toolkit_expectation"]
        assert expectation["publication_expectation"]

    outputs = []
    for scenario in fixture["scenarios"]:
        actual = evaluate(scenario, fixture)
        assert actual == scenario["expected"], (scenario["id"], actual, scenario["expected"])
        outputs.append({"id": scenario["id"], **actual})
    assert outputs[0]["status"] == "PASS_DEPENDENCY_GATE_REVIEW_ONLY"
    assert all(item["status"] == "BLOCKED_DEPENDENCY" for item in outputs[1:5])
    assert outputs[5]["reason"] == "REJECT_NEGATIVE_HOLDOUT"
    assert outputs[6]["reason"] == "REJECT_WIDENED_CLAIM_CEILING"
    print(json.dumps({"status":"PASS_DEPENDENCY_GATE_FIXTURE","candidate_rows":40,"scenarios":len(outputs),"results":outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
