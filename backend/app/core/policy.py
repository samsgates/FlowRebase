from __future__ import annotations

from typing import Any

import httpx

from .uam import UAMPolicy, UAMProcess


class PolicyDecision(dict):
    @property
    def allowed(self) -> bool:
        return bool(self.get("allowed"))


class PolicyEngine:
    def __init__(self, opa_url: str | None = None):
        self.opa_url = opa_url.rstrip("/") if opa_url else None

    async def evaluate(self, process: UAMProcess, action: str, context: dict[str, Any]) -> PolicyDecision:
        if self.opa_url:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    f"{self.opa_url}/v1/data/flowrebase/decision",
                    json={"input": {"action": action, "context": context, "process": process.model_dump(mode="json")}},
                )
                response.raise_for_status()
                result = response.json().get("result", {})
                return PolicyDecision(result)
        return self._local(process.policies, action, context)

    def _local(self, policies: list[UAMPolicy], action: str, context: dict[str, Any]) -> PolicyDecision:
        matching = [p for p in policies if p.action == action and self._matches(p.when, context)]
        denies = [p for p in matching if p.effect == "deny"]
        approvals = [p for p in matching if p.effect == "require_approval"]
        if denies:
            return PolicyDecision(allowed=False, requires_approval=False, reasons=[p.reason or p.name for p in denies])
        if approvals:
            return PolicyDecision(allowed=True, requires_approval=True, reasons=[p.reason or p.name for p in approvals])
        return PolicyDecision(allowed=True, requires_approval=False, reasons=[])

    def _matches(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        for key, value in expected.items():
            observed = actual.get(key)
            if isinstance(value, dict):
                if "gt" in value and not (observed is not None and observed > value["gt"]):
                    return False
                if "gte" in value and not (observed is not None and observed >= value["gte"]):
                    return False
                if "eq" in value and observed != value["eq"]:
                    return False
                if "in" in value and observed not in value["in"]:
                    return False
            elif observed != value:
                return False
        return True
