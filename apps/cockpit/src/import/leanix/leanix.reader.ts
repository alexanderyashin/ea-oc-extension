// apps/cockpit/src/import/leanix/leanix.reader.ts
type FileTextMap = Record<string, string>;

function normalizePath(p: string): string {
  return p.replaceAll("\\", "/").replace(/^\/+/, "");
}

async function readFileText(f: File): Promise<string> {
  return await f.text();
}

async function walkDir(
  dir: FileSystemDirectoryHandle,
  prefix: string,
  out: FileTextMap
): Promise<void> {
  for await (const [name, handle] of (dir as any).entries()) {
    const rel = normalizePath(prefix ? `${prefix}/${name}` : name);
    if (handle.kind === "directory") {
      await walkDir(handle as FileSystemDirectoryHandle, rel, out);
    } else if (handle.kind === "file") {
      const file = await (handle as FileSystemFileHandle).getFile();
      out[rel] = await readFileText(file);
    }
  }
}

/**
 * Read LeanIX-like fixture folder/files into a stable map:
 * { "fact_sheets/applications.csv": "...", "relations/app_to_capability.csv": "...", "manifest.json": "..." }
 */
export async function readLeanixCsvSources(opts: {
  // preferred (Chromium): directory handle
  directoryHandle?: FileSystemDirectoryHandle | null;
  // fallback: file list (webkitdirectory or multi-file)
  files?: FileList | File[] | null;
}): Promise<FileTextMap> {
  const out: FileTextMap = {};

  if (opts.directoryHandle) {
    await walkDir(opts.directoryHandle, "", out);
    return out;
  }

  const filesArr = Array.isArray(opts.files)
    ? opts.files
    : opts.files
      ? Array.from(opts.files)
      : [];

  for (const f of filesArr) {
    // webkitRelativePath is stable for webkitdirectory selection
    const rel = normalizePath((f as any).webkitRelativePath || f.name);
    out[rel] = await readFileText(f);
  }

  return out;
}

export function supportsDirectoryPicker(): boolean {
  return typeof (window as any).showDirectoryPicker === "function";
}

export async function pickDirectory(): Promise<FileSystemDirectoryHandle | null> {
  if (!supportsDirectoryPicker()) return null;
  try {
    const h = await (window as any).showDirectoryPicker();
    return h as FileSystemDirectoryHandle;
  } catch {
    return null;
  }
}
