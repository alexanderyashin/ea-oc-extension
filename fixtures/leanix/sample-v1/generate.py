from __future__ import annotations

import csv
import os
import random
from dataclasses import dataclass
from typing import Iterable, List, Tuple

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_FACT = os.path.join(ROOT, "fact_sheets")
OUT_REL = os.path.join(ROOT, "relations")

SEED = 1337

# Counts (≈200 objects total)
N_APP = 60
N_ITC = 40
N_CAP = 35
N_PROV = 25
N_DATA = 40

random.seed(SEED)

@dataclass(frozen=True)
class Row:
    id: str
    name: str
    type: str
    lifecycle: str
    status: str
    description: str

LIFECYCLES = ["Plan", "Phase In", "Active", "Phase Out", "Retire"]
STATUS = ["Active", "Planned", "Deprecated"]

def ensure_dirs() -> None:
    os.makedirs(OUT_FACT, exist_ok=True)
    os.makedirs(OUT_REL, exist_ok=True)

def write_csv(path: str, header: List[str], rows: Iterable[List[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def mk_id(prefix: str, i: int) -> str:
    return f"{prefix}-{i:03d}"

def pick(seq: List[str]) -> str:
    return random.choice(seq)

def gen_fact_sheets() -> Tuple[List[Row], List[Row], List[Row], List[Row], List[Row]]:
    apps: List[Row] = []
    itcs: List[Row] = []
    caps: List[Row] = []
    prov: List[Row] = []
    data: List[Row] = []

    # Applications
    for i in range(1, N_APP + 1):
        rid = mk_id("APP", i)
        name = f"Application {i:02d}"
        apps.append(Row(
            id=rid,
            name=name,
            type="Application",
            lifecycle=pick(LIFECYCLES),
            status=pick(STATUS),
            description=f"Synthetic application for import/parsing tests ({rid})."
        ))

    # IT Components
    for i in range(1, N_ITC + 1):
        rid = mk_id("ITC", i)
        name = f"IT Component {i:02d}"
        itcs.append(Row(
            id=rid,
            name=name,
            type="ITComponent",
            lifecycle=pick(LIFECYCLES),
            status=pick(STATUS),
            description=f"Synthetic IT component for tests ({rid})."
        ))

    # Business Capabilities
    for i in range(1, N_CAP + 1):
        rid = mk_id("BC", i)
        name = f"Business Capability {i:02d}"
        caps.append(Row(
            id=rid,
            name=name,
            type="BusinessCapability",
            lifecycle="Active",
            status="Active",
            description=f"Synthetic business capability ({rid})."
        ))

    # Providers
    for i in range(1, N_PROV + 1):
        rid = mk_id("PRV", i)
        name = f"Provider {i:02d}"
        prov.append(Row(
            id=rid,
            name=name,
            type="Provider",
            lifecycle="Active",
            status="Active",
            description=f"Synthetic provider ({rid})."
        ))

    # Data Objects
    for i in range(1, N_DATA + 1):
        rid = mk_id("DO", i)
        name = f"Data Object {i:02d}"
        data.append(Row(
            id=rid,
            name=name,
            type="DataObject",
            lifecycle=pick(LIFECYCLES),
            status=pick(STATUS),
            description=f"Synthetic data object ({rid})."
        ))

    return apps, itcs, caps, prov, data

def write_fact_sheets(apps: List[Row], itcs: List[Row], caps: List[Row], prov: List[Row], data: List[Row]) -> None:
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

def rel_rows(source_ids: List[str], target_ids: List[str], min_links: int, max_links: int, relation_type: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for sid in source_ids:
        k = random.randint(min_links, max_links)
        targets = random.sample(target_ids, k=min(k, len(target_ids)))
        for tid in targets:
            rows.append([sid, tid, relation_type])
    return rows

def write_relations(apps: List[Row], itcs: List[Row], caps: List[Row], prov: List[Row], data: List[Row]) -> None:
    header = ["source_id", "target_id", "relation_type"]
    app_ids = [r.id for r in apps]
    itc_ids = [r.id for r in itcs]
    cap_ids = [r.id for r in caps]
    prv_ids = [r.id for r in prov]
    do_ids  = [r.id for r in data]

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
        if k == 0:
            continue
        targets = random.sample(prv_ids, k=min(k, len(prv_ids)))
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
    ensure_dirs()
    apps, itcs, caps, prov, data = gen_fact_sheets()
    write_fact_sheets(apps, itcs, caps, prov, data)
    write_relations(apps, itcs, caps, prov, data)
    print("OK: generated fixtures/leanix/sample-v1/*")

if __name__ == "__main__":
    main()
