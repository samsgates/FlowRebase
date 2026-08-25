from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .runtime import UAMRuntime
from .uam import UAMProcess


@dataclass
class CaseResult:
    name: str
    passed: bool
    score: float
    critical_failure: bool
    differences: list[dict]
    actual: dict[str, Any]
    trace: list[dict]


class ProofRunEngine:
    def __init__(self):
        self.runtime = UAMRuntime()

    def run(self, process: UAMProcess, cases: list[dict]) -> dict:
        results: list[CaseResult] = []
        for case in cases:
            execution = self.runtime.execute(process, case.get("input", {}))
            actual = execution["output"]
            expected = case.get("expected", {})
            critical_paths = set(case.get("critical_paths", []))
            differences: list[dict] = []
            matches = 0
            total = max(1, len(expected))
            critical_failure = False
            for key, expected_value in expected.items():
                actual_value = actual.get(key)
                if actual_value == expected_value:
                    matches += 1
                else:
                    is_critical = key in critical_paths
                    critical_failure = critical_failure or is_critical
                    differences.append(
                        {
                            "path": key,
                            "expected": expected_value,
                            "actual": actual_value,
                            "critical": is_critical,
                        }
                    )
            score = matches / total * 100
            results.append(
                CaseResult(
                    name=case.get("name", "case"),
                    passed=not differences,
                    score=score,
                    critical_failure=critical_failure,
                    differences=differences,
                    actual=actual,
                    trace=execution["trace"],
                )
            )

        overall = sum(r.score for r in results) / max(1, len(results))
        critical = any(r.critical_failure for r in results)
        passed = bool(results) and all(r.passed for r in results) and not critical
        return {
            "status": "passed" if passed else "failed",
            "score": round(overall, 2),
            "critical_failure": critical,
            "cases": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "score": r.score,
                    "critical_failure": r.critical_failure,
                    "differences": r.differences,
                    "actual": r.actual,
                    "trace": r.trace,
                }
                for r in results
            ],
        }
