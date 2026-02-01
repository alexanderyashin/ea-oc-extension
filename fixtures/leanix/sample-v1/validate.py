# fixtures/leanix/sample-v1/validate.py
from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple


ROOT = os.path.dirname(os.path.abspath(__file__))
FACT = os.path.join(ROOT, "fact_sheets")
REL = os.path.join(ROOT, "relations")


@dataclass(frozen=True)
class CsvSpec:
    path: str
    required_cols: Tuple[str, ...]


FACT_SPECS: Dict[str, CsvSpec] = {
    "applications.csv": CsvSpec(
        os.path.join(FACT, "applications.csv"),
        ("id", "name", "type", "lifecycle", "status", "description"),
    ),
    "it_components.csv": CsvSpec(
        os.path.join(FACT, "it_components.csv"),
        ("id", "name", "type", "lifecycle", "status", "description"),
    ),
    "business_capabilities.csv": CsvSpec(
        os.path.join(FACT, "business_capabilities.csv"),
        ("id", "name", "type", "lifecycle", "status", "description"),
    ),
    "providers.csv": CsvSpec(
        os.path.join(FACT, "providers.csv"),
        ("id", "name", "type", "lifecycle", "status", "description"),
    ),
    "data_objects.csv": CsvSpec(
        os.path.join(FACT, "data_objects.csv"),
        ("id", "name", "type", "lifecycle", "status", "description"),
    ),
}

REL_SPECS: Dict[str, CsvSpec] = {
    "app_to_capability.csv": CsvSpec(
        os.path.join(REL, "app_to_capability.csv"),
        ("source_id", "target_id", "relation_type"),
    ),
    "app_to_it_component.csv": CsvSpec(
        os.path.join(REL, "app_to_it_component.csv"),
        ("source_id", "target_id", "relation_type"),
    ),
    "app_to_provider.csv": CsvSpec(
        os.path.join(REL, "app_to_provider.csv"),
        ("source_id", "target_id", "relation_type"),
    ),
    "app_to_data_object.csv": CsvSpec(
        os.path.join(REL, "app_to_data_object.csv"),
        ("source_id", "target_id", "relation_type"),
    ),
}


def die(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(2)


def read_csv(spec: CsvSpec) -> List[Dict[str, str]]:
    if not os.path.exists(spec.path):
        die(f"missing file: {spec.path}")

    with open(spec.path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            die(f"empty header: {spec.path}")

        fieldnames = [c.strip() for c in r.fieldnames]
        missing = [c for c in spec.required_cols if c not in fieldnames]
        if missing:
            die(f"missing columns in {os.path.basename(spec.path)}: {missing}")

        rows: List[Dict[str, str]] = []
        for row in r:
            # Normalize keys + trim values
            norm = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            rows.append(norm)
        return rows


def require_non_empty(rows: List[Dict[str, str]], file_label: str) -> None:
    if len(rows) == 0:
        die(f"{file_label} has zero data rows")


def ensure_unique_ids(rows: List[Dict[str, str]], file_label: str) -> Set[str]:
    ids: List[str] = []
    for i, row in enumerate(rows, start=1):
        rid = (row.get("id") or "").strip()
        if not rid:
            die(f"{file_label}: row {i} has empty id")
        ids.append(rid)

    s = set(ids)
    if len(s) != len(ids):
        die(f"{file_label}: duplicate ids detected")
    return s


def validate_fact_sheets() -> Dict[str, Set[str]]:
    # Returns id sets by type key
    app_rows = read_csv(FACT_SPECS["applications.csv"])
    itc_rows = read_csv(FACT_SPECS["it_components.csv"])
    bc_rows = read_csv(FACT_SPECS["business_capabilities.csv"])
    prv_rows = read_csv(FACT_SPECS["providers.csv"])
    do_rows = read_csv(FACT_SPECS["data_objects.csv"])

    require_non_empty(app_rows, "applications.csv")
    require_non_empty(itc_rows, "it_components.csv")
    require_non_empty(bc_rows, "business_capabilities.csv")
    require_non_empty(prv_rows, "providers.csv")
    require_non_empty(do_rows, "data_objects.csv")

    app_ids = ensure_unique_ids(app_rows, "applications.csv")
    itc_ids = ensure_unique_ids(itc_rows, "it_components.csv")
    bc_ids = ensure_unique_ids(bc_rows, "business_capabilities.csv")
    prv_ids = ensure_unique_ids(prv_rows, "providers.csv")
    do_ids = ensure_unique_ids(do_rows, "data_objects.csv")

    return {
        "APP": app_ids,
        "ITC": itc_ids,
        "BC": bc_ids,
        "PRV": prv_ids,
        "DO": do_ids,
    }


def validate_relations(id_sets: Dict[str, Set[str]]) -> Dict[str, int]:
    def check_rows(
        file_label: str, rows: List[Dict[str, str]], sources: Set[str], targets: Set[str]
    ) -> int:
        require_non_empty(rows, file_label)

        bad: List[str] = []
        for i, row in enumerate(rows, start=1):
            sid = (row.get("source_id") or "").strip()
            tid = (row.get("target_id") or "").strip()
            rty = (row.get("relation_type") or "").strip()

            if not sid or not tid or not rty:
                bad.append(f"{file_label}: row {i} has empty fields")
                continue
            if sid not in sources:
                bad.append(f"{file_label}: row {i} unknown source_id {sid}")
            if tid not in targets:
                bad.append(f"{file_label}: row {i} unknown target_id {tid}")

        if bad:
            # Print only first ~20 to keep output readable
            preview = "\n".join(bad[:20])
            die(f"{file_label}: integrity errors:\n{preview}")

        return len(rows)

    counts: Dict[str, int] = {}

    r_cap = read_csv(REL_SPECS["app_to_capability.csv"])
    counts["app_to_capability.csv"] = check_rows(
        "app_to_capability.csv", r_cap, id_sets["APP"], id_sets["BC"]
    )

    r_itc = read_csv(REL_SPECS["app_to_it_component.csv"])
    counts["app_to_it_component.csv"] = check_rows(
        "app_to_it_component.csv", r_itc, id_sets["APP"], id_sets["ITC"]
    )

    r_prv = read_csv(REL_SPECS["app_to_provider.csv"])
    # provider links may be sparse, but file must exist and be structurally valid
    # still require non-empty because generator produces some provider links
    counts["app_to_provider.csv"] = check_rows(
        "app_to_provider.csv", r_prv, id_sets["APP"], id_sets["PRV"]
    )

    r_do = read_csv(REL_SPECS["app_to_data_object.csv"])
    counts["app_to_data_object.csv"] = check_rows(
        "app_to_data_object.csv", r_do, id_sets["APP"], id_sets["DO"]
    )

    return counts


def main() -> None:
    # Basic layout
    if not os.path.isdir(FACT):
        die(f"missing directory: {FACT}")
    if not os.path.isdir(REL):
        die(f"missing directory: {REL}")

    id_sets = validate_fact_sheets()
    rel_counts = validate_relations(id_sets)

    print("[OK] dataset looks structurally valid.")
    print("Counts:")
    print(f"  APP: {len(id_sets['APP'])}")
    print(f"  ITC: {len(id_sets['ITC'])}")
    print(f"  BC:  {len(id_sets['BC'])}")
    print(f"  PRV: {len(id_sets['PRV'])}")
    print(f"  DO:  {len(id_sets['DO'])}")
    for k in ("app_to_capability.csv", "app_to_it_component.csv", "app_to_provider.csv", "app_to_data_object.csv"):
        print(f"  {k}: {rel_counts[k]} links")


if __name__ == "__main__":
    main()
