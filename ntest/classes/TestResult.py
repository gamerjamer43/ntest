# huge wip
from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    file: str
    passed: bool
    duration: float
    error: str | None