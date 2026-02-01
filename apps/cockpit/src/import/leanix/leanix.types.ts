// apps/cockpit/src/import/leanix/leanix.types.ts

export type LeanixFactSheetKind =
  | "applications"
  | "it_components"
  | "business_capabilities"
  | "providers"
  | "data_objects";

export type LeanixRelationKind =
  | "app_to_capability"
  | "app_to_it_component"
  | "app_to_provider"
  | "app_to_data_object";

export type LeanixFactSheetRow = {
  id: string;
  name: string;
  // full original row, normalized header keys
  raw: Record<string, string>;
};

export type LeanixRelationRow = {
  fromId: string;
  toId: string;
  raw: Record<string, string>;
};

export type LeanixSnapshot = {
  manifest: {
    version: string; // "unknown" if missing
    // keep raw manifest json (if any) for diagnostics, without semantics
    raw?: unknown;
  };
  factSheets: Record<LeanixFactSheetKind, LeanixFactSheetRow[]>;
  relations: Record<LeanixRelationKind, LeanixRelationRow[]>;
  // file inventory (relative path -> bytes)
  files: Record<string, { bytes: number }>;
};
