// apps/cockpit/src/import/leanix/leanix.parser.ts

export type CsvTable = {
  headers: string[]; // original headers (trimmed)
  rows: string[][];  // raw row fields, same length as headers (padded)
};

function stripBom(s: string): string {
  if (s.charCodeAt(0) === 0xfeff) return s.slice(1);
  return s;
}

export function parseCsv(text: string): CsvTable {
  const s = stripBom(text ?? "");
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let inQuotes = false;

  function pushField() {
    row.push(field);
    field = "";
  }
  function pushRow() {
    // avoid trailing empty last row caused by final newline
    if (row.length === 1 && row[0] === "" && rows.length === 0) {
      // header-only empty -> keep (will fail later)
    }
    rows.push(row);
    row = [];
  }

  for (let i = 0; i < s.length; i++) {
    const c = s[i];

    if (inQuotes) {
      if (c === '"') {
        const next = s[i + 1];
        if (next === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += c;
      }
      continue;
    }

    // not in quotes
    if (c === '"') {
      inQuotes = true;
      continue;
    }

    if (c === ",") {
      pushField();
      continue;
    }

    if (c === "\r") {
      // handle CRLF
      const next = s[i + 1];
      if (next === "\n") i++;
      pushField();
      pushRow();
      continue;
    }

    if (c === "\n") {
      pushField();
      pushRow();
      continue;
    }

    field += c;
  }

  // last field/row
  pushField();
  pushRow();

  // remove final empty row if it is completely empty (common trailing newline)
  const last = rows[rows.length - 1];
  if (last && last.every((x) => x === "") && rows.length > 1) rows.pop();

  const headersRaw = rows.length > 0 ? rows[0] : [];
  const headers = headersRaw.map((h) => String(h ?? "").trim());

  const dataRows = rows.slice(1).map((r) => {
    const rr = r.map((x) => String(x ?? ""));
    while (rr.length < headers.length) rr.push("");
    if (rr.length > headers.length) rr.length = headers.length;
    return rr;
  });

  return { headers, rows: dataRows };
}

export function tableToObjects(t: CsvTable): Array<Record<string, string>> {
  const keys = t.headers.map((h) => h.trim());
  const normKeys = keys.map((k) => normalizeKey(k));

  return t.rows.map((r) => {
    const obj: Record<string, string> = {};
    for (let i = 0; i < normKeys.length; i++) {
      obj[normKeys[i]] = String(r[i] ?? "").trim();
    }
    return obj;
  });
}

export function normalizeKey(k: string): string {
  return String(k ?? "").trim().toLowerCase();
}
