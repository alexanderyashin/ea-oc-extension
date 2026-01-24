from dataclasses import dataclass

STOP_EXIT_CODE = 2
END_EXIT_CODE = 0
USAGE_EXIT_CODE = 1

FORBIDDEN = (
    "advice", "recommend", "optimize", "retry", "recover",
    "control", "tune", "kpi", "heal"
)

@dataclass(frozen=True)
class Stop:
    reason: str
    details: str | None = None

    def format(self) -> str:
        return f"STOP: {self.reason}" + (f"\nDETAILS: {self.details}" if self.details else "")

def detect_forbidden_semantics(argv):
    joined = " ".join(argv).lower()
    for f in FORBIDDEN:
        if f in joined:
            return Stop("Forbidden CLI semantics", f)
    return None
