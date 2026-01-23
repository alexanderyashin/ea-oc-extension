class InvariantViolation(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvariantViolation(message)
