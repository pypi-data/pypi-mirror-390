from enum import Enum

class SatResult(Enum):
    SAT = "sat"
    UNSAT = "unsat"
    UNKNOWN = "unknown"

    def __bool__(self) -> bool:
        return self.value == SatResult.SAT.value

__all__ = [
    "SatResult",
]
