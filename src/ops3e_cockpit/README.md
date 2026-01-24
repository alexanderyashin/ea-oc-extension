# OPS-CHILD-E — Read-Only Diagnostic Cockpit

## Hard boundaries (non-negotiable)
- **READ-ONLY**: no engine calls, no file writes.
- **DIAGNOSTIC-ONLY**: visualization only, no advice/control.
- **NO CONTROL**: no action buttons (no replay/recovery/optimization).
- **NO STATE**: no localStorage/sessionStorage/IndexedDB/cookies/service workers.

## Inputs (ONLY)
Place artefacts under `src/ops3e_cockpit/data/`:
- `trace.json`
- `graph.json` (preferred) OR `graph.dot` (fallback: displayed as raw text only)
- optional: `spec.yaml` (metadata shown as raw text)

## Run (static)
```powershell
Set-Location src/ops3e_cockpit
python -m http.server 8000

Open:

http://localhost:8000/index.html

STOP transparency

STOP is always visible:

Trace header badge + STOP reason

Step list (STOP step)

Graph: STOP node highlighted if present in graph.json (kind=STOP or id=STOP)


---

## OPTIONAL FILE: `src/ops3e_cockpit/render_dist.py`  
(Не нужен для работы, но помогает собрать “копируемую” папку `dist/`. Всё равно read-only: только копирование уже существующих файлов.)

```python
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

def main() -> None:
    DIST.mkdir(exist_ok=True)

    for name in ["index.html", "styles.css", "app.js", "README.md"]:
        shutil.copy2(ROOT / name, DIST / name)

    data = ROOT / "data"
    if data.exists():
        dst_data = DIST / "data"
        dst_data.mkdir(exist_ok=True)
        for f in data.glob("*"):
            if f.is_file():
                shutil.copy2(f, dst_data / f.name)

    print(f"dist ready: {DIST}")

if __name__ == "__main__":
    main()
