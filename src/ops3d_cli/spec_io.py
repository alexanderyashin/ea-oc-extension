import json
from pathlib import Path
from dataclasses import dataclass
from ops3d_cli.policy import Stop

@dataclass(frozen=True)
class LoadedSpec:
    path: Path
    obj: dict
    format: str

def load_spec(path: str):
    p = Path(path)
    if not p.is_file():
        return Stop("Invalid spec", "File not found")

    try:
        if p.suffix in (".yaml", ".yml"):
            import yaml
            data = yaml.safe_load(p.read_text())
        elif p.suffix == ".json":
            data = json.loads(p.read_text())
        else:
            return Stop("Invalid spec", "Unsupported extension")
    except Exception as e:
        return Stop("Invalid spec", str(e))

    if not isinstance(data, dict):
        return Stop("Invalid spec", "Top-level must be mapping")

    return LoadedSpec(p, data, p.suffix)
