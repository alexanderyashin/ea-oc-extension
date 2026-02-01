// apps/cockpit/src/import/types.ts
export type SourceKind = "leanix_csv";

export type DiagnosticReport = {
  errors: string[];
  warnings: string[];
};

export type SourceSnapshot<TPayload = unknown> = {
  kind: SourceKind;
  version: string; // from manifest.json if present, else "unknown"
  counts: Record<string, number>;
  payload: TPayload;
  diagnostics: DiagnosticReport;
};
