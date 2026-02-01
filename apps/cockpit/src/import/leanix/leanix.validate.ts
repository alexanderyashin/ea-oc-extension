// apps/cockpit/src/import/leanix/leanix.validate.ts
import type { DiagnosticReport } from "../types";
import type {
  LeanixFactSheetKind,
  LeanixRelationKind,
  LeanixSnapshot,
} from "./leanix.types";

export type LeanixValidationPolicy = {
  // for this MVP fixture: broken references are fatal
  brokenReferencesAreFatal: boolean;
};

export const DEFAULT_POLICY: LeanixValidationPolicy = {
  brokenReferencesAreFatal: true,
};

const REQUIRED_FILES: string[] = [
  "manifest.json",

  "fact_sheets/applications.csv",
  "fact_sheets/it_components.csv",
  "fact_sheets/business_capabilities.csv",
  "fact_sheets/providers.csv",
  "fact_sheets/data_objects.csv",

  "relations/app_to_capability.csv",
  "relations/app_to_it_component.csv",
  "relations/app_to_provider.csv",
  "relations/app_to_data_object.csv",
];

// Minimal header requirements (normalized keys)
const FACT_REQUIRED_HEADERS = ["id", "name"];

function normalizePath(p: string): string {
  return p.replaceAll("\\", "/").replace(/^\/+/, "");
}

export function validateLeanixSnapshot(
  filesMap: Record<string, string>,
  snapshot: LeanixSnapshot,
  report: DiagnosticReport,
  policy: LeanixValidationPolicy = DEFAULT_POLICY
): DiagnosticReport {
  const errors = report.errors;
  const warnings = report.warnings;

  // 1) required files
  const keys = new Set(Object.keys(filesMap).map(normalizePath));
  for (const req of REQUIRED_FILES) {
    if (!keys.has(req)) {
      errors.push(`Missing required file: ${req}`);
    }
  }

  // 2) required headers (fact sheets)
  const fsKinds: Array<[LeanixFactSheetKind, string]> = [
    ["applications", "fact_sheets/applications.csv"],
    ["it_components", "fact_sheets/it_components.csv"],
    ["business_capabilities", "fact_sheets/business_capabilities.csv"],
    ["providers", "fact_sheets/providers.csv"],
    ["data_objects", "fact_sheets/data_objects.csv"],
  ];

  for (const [kind, path] of fsKinds) {
    const rows = snapshot.factSheets[kind] ?? [];
    if (!keys.has(path)) continue;

    // header presence was already checked by parser indirectly; here we check row fields existence
    // We require id/name to be present and non-empty at least for some rows.
    if (rows.length === 0) warnings.push(`Fact sheet has 0 rows: ${path}`);

    // check each row has required keys
    for (const h of FACT_REQUIRED_HEADERS) {
      const hasAny = rows.some((r) => (r.raw?.[h] ?? "").length > 0);
      if (!hasAny) errors.push(`Missing required header "${h}" in ${path} (normalized)`);
    }

    // uniqueness of id
    const seen = new Set<string>();
    for (const r of rows) {
      const id = String(r.id ?? "").trim();
      if (!id) {
        errors.push(`Empty id in ${path}`);
        continue;
      }
      if (seen.has(id)) errors.push(`Duplicate id "${id}" in ${path}`);
      seen.add(id);
    }
  }

  // 3) relations: referential integrity (against applications + targets)
  const appIds = new Set(snapshot.factSheets.applications.map((x) => x.id));

  const targetSets: Record<LeanixRelationKind, Set<string>> = {
    app_to_capability: new Set(snapshot.factSheets.business_capabilities.map((x) => x.id)),
    app_to_it_component: new Set(snapshot.factSheets.it_components.map((x) => x.id)),
    app_to_provider: new Set(snapshot.factSheets.providers.map((x) => x.id)),
    app_to_data_object: new Set(snapshot.factSheets.data_objects.map((x) => x.id)),
  };

  const relPaths: Record<LeanixRelationKind, string> = {
    app_to_capability: "relations/app_to_capability.csv",
    app_to_it_component: "relations/app_to_it_component.csv",
    app_to_provider: "relations/app_to_provider.csv",
    app_to_data_object: "relations/app_to_data_object.csv",
  };

  (Object.keys(relPaths) as LeanixRelationKind[]).forEach((rk) => {
    const rows = snapshot.relations[rk] ?? [];
    const path = relPaths[rk];
    if (!keys.has(path)) return;

    if (rows.length === 0) warnings.push(`Relation sheet has 0 rows: ${path}`);

    for (const r of rows) {
      const from = String(r.fromId ?? "").trim();
      const to = String(r.toId ?? "").trim();

      if (!from || !to) {
        errors.push(`Empty from/to in ${path}`);
        continue;
      }

      if (!appIds.has(from)) {
        const msg = `Broken reference: application "${from}" not found (in ${path})`;
        if (policy.brokenReferencesAreFatal) errors.push(msg);
        else warnings.push(msg);
      }

      if (!targetSets[rk].has(to)) {
        const msg = `Broken reference: target "${to}" not found for ${rk} (in ${path})`;
        if (policy.brokenReferencesAreFatal) errors.push(msg);
        else warnings.push(msg);
      }
    }
  });

  return { errors, warnings };
}
