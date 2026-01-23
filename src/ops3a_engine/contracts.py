class ContractViolation(Exception):
    pass


class ExtensionRegistry:
    """
    Explicit allowlist for engine extensions.
    Anything not registered is forbidden.
    """

    def __init__(self) -> None:
        self._allowed = set()

    def allow(self, name: str) -> None:
        self._allowed.add(name)

    def require_allowed(self, name: str) -> None:
        if name not in self._allowed:
            raise ContractViolation(f"Forbidden extension: {name}")
