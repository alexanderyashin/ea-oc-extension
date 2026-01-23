class StateViolation(Exception):
    pass


class EngineState:
    INIT = "INIT"
    RUN = "RUN"
    END = "END"
    STOP = "STOP"


class ExecutionStateMachine:
    """
    INIT → RUN → END | STOP
    STOP is terminal and irreversible.
    """

    def __init__(self) -> None:
        self._state = EngineState.INIT

    @property
    def state(self) -> str:
        return self._state

    def start(self) -> None:
        if self._state != EngineState.INIT:
            raise StateViolation("start() allowed only from INIT")
        self._state = EngineState.RUN

    def stop(self) -> None:
        self._state = EngineState.STOP

    def end(self) -> None:
        if self._state != EngineState.RUN:
            raise StateViolation("end() allowed only from RUN")
        self._state = EngineState.END
