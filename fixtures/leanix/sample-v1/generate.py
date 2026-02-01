# fixtures/leanix/sample-v1/generate.py
from __future__ import annotations

import csv
import os
import random
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


# ----------------------------
# Output layout
# ----------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))

OUT_FACT = os.path.join(ROOT, "fact_sheets")
OUT_REL = os.path.join(ROOT, "relations")

SEED = 1337

# Counts (≈200 objects total)
N_APP = 60
N_ITC = 40
N_CAP = 35
N_PROV = 15
N_DATA = 50

LIFECYCLES = ["Plan", "PhaseIn", "Active", "PhaseOut", "EndOfLife"]
STATUS = ["Active", "Inactive", "Planned"]


@dataclass(frozen=True)
class Row:
    id: str
    name: str
    type: str
    lifecycle: str
    status: str
    description: str


def ensure_dirs() -> None:
    os.makedirs(OUT_FACT, exist_ok=True)
    os.makedirs(OUT_REL, exist_ok=True)


def mk_id(prefix: str, i: int) -> str:
    return f"{prefix}-{i:04d}"


def pick(xs: Sequence[str]) -> str:
    return random.choice(xs)


def write_csv(path: str, header: List[str], rows: Iterable[Sequence[str]]) -> None:
    # newline="" is important on Windows to avoid blank lines
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(list(r))


def gen_fact_sheets() -> Tuple[List[Row], List[Row], List[Row], List[Row], List[Row]]:
    apps: List[Row] = []
    itcs: List[Row] = []
    caps: List[Row] = []
    prov: List[Row] = []
    data: List[Row] = []

    for i in range(1, N_APP + 1):
        rid = mk_id("APP", i)
        apps.append(
            Row(
                rid,
                f"Application {i:02d}",
                "Application",
                pick(LIFECYCLES),
                pick(STATUS),
                f"Synthetic application for import/parsing tests ({rid}).",
            )
        )

    for i in range(1, N_ITC + 1):
        rid = mk_id("ITC", i)
        itcs.append(
            Row(
                rid,
                f"IT Component {i:02d}",
                "ITComponent",
                pick(LIFECYCLES),
                pick(STATUS),
                f"Synthetic IT component for tests ({rid}).",
            )
        )

    for i in range(1, N_CAP + 1):
        rid = mk_id("BC", i)
        caps.append(
            Row(
                rid,
                f"Business Capability {i:02d}",
                "BusinessCapability",
                "Active",
                "Active",
                f"Synthetic business capability ({rid}).",
            )
        )

    for i in range(1, N_PROV + 1):
        rid = mk_id("PRV", i)
        prov.append(
            Row(
                rid,
                f"Provider {i:02d}",
                "Provider",
                "Active",
                "Active",
                f"Synthetic provider ({rid}).",
            )
        )

    for i in range(1, N_DATA + 1):
        rid = mk_id("DO", i)
        data.append(
            Row(
                rid,
                f"Data Object {i:02d}",
                "DataObject",
                pick(LIFECYCLES),
                pick(STATUS),
                f"Synthetic data object ({rid}).",
            )
        )

    return apps, itcs, caps, prov, data


def write_fact_sheets(
    apps: List[Row],
    itcs: List[Row],
    caps: List[Row],
    prov: List[Row],
    data: List[Row],
) -> None:
    header = ["id", "name", "type", "lifecycle", "status", "description"]

    write_csv(
        os.path.join(OUT_FACT, "applications.csv"),
        header,
        ([r.id, r.name, r.type, r.lifecycle, r.status, r.description] for r in apps),
    )
    write_csv(
        os.path.join(OUT_FACT, "it_components.csv"),
        header,
        ([r.id, r.name, r.type, r.lifecycle, r.status, r.description] for r in itcs),
    )
    write_csv(
        os.path.join(OUT_FACT, "business_capabilities.csv"),
        header,
        ([r.id, r.name, r.type, r.lifecycle, r.status, r.description] for r in caps),
    )
    write_csv(
        os.path.join(OUT_FACT, "providers.csv"),
        header,
        ([r.id, r.name, r.type, r.lifecycle, r.status, r.description] for r in prov),
    )
    write_csv(
        os.path.join(OUT_FACT, "data_objects.csv"),
        header,
        ([r.id, r.name, r.type, r.lifecycle, r.status, r.description] for r in data),
    )


def rel_rows(
    source_ids: List[str],
    target_ids: List[str],
    min_links: int,
    max_links: int,
    relation_type: str,
) -> List[List[str]]:
    rows: List[List[str]] = []
    for sid in source_ids:
        k = random.randint(min_links, max_links)
        k = min(k, len(target_ids))
        targets = random.sample(target_ids, k=k)
        for tid in targets:
            rows.append([sid, tid, relation_type])
    return rows


def write_relations(
    apps: List[Row],
    itcs: List[Row],
    caps: List[Row],
    prov: List[Row],
    data: List[Row],
) -> None:
    header = ["source_id", "target_id", "relation_type"]

    app_ids = [r.id for r in apps]
    itc_ids = [r.id for r in itcs]
    cap_ids = [r.id for r in caps]
    prv_ids = [r.id for r in prov]
    do_ids = [r.id for r in data]

    # App ↔ Capability: 1..3 per app
    write_csv(
        os.path.join(OUT_REL, "app_to_capability.csv"),
        header,
        rel_rows(app_ids, cap_ids, 1, 3, "supports"),
    )

    # App ↔ IT Component: 2..5 per app
    write_csv(
        os.path.join(OUT_REL, "app_to_it_component.csv"),
        header,
        rel_rows(app_ids, itc_ids, 2, 5, "uses"),
    )

    # App ↔ Provider: 0..2 per app (not every app has a provider)
    rows_prv: List[List[str]] = []
    for sid in app_ids:
        k = random.randint(0, 2)
        k = min(k, len(prv_ids))
        if k <= 0:
            continue
        targets = random.sample(prv_ids, k=k)
        for tid in targets:
            rows_prv.append([sid, tid, "depends_on"])

    write_csv(
        os.path.join(OUT_REL, "app_to_provider.csv"),
        header,
        rows_prv,
    )

    # App ↔ Data Object: 1..4 per app
    write_csv(
        os.path.join(OUT_REL, "app_to_data_object.csv"),
        header,
        rel_rows(app_ids, do_ids, 1, 4, "reads_writes"),
    )


def main() -> None:
    random.seed(SEED)
    ensure_dirs()

    apps, itcs, caps, prov, data = gen_fact_sheets()
    write_fact_sheets(apps, itcs, caps, prov, data)
    write_relations(apps, itcs, caps, prov, data)


if __name__ == "__main__":
    main()
