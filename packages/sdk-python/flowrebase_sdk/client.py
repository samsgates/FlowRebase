from __future__ import annotations

from typing import Any

import httpx


class FlowRebaseClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: float = 30):
        self.base_url = base_url.rstrip("/") + "/api/v1"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def portfolio(self) -> dict[str, Any]:
        return self._get("/portfolio/summary")

    def automations(self) -> list[dict[str, Any]]:
        return self._get("/automations")

    def import_automation(self, name: str, source_type: str, content: str, metadata: dict | None = None) -> dict[str, Any]:
        return self._post("/automations/import", {"name": name, "source_type": source_type, "content": content, "metadata": metadata or {}})

    def recommend(self, automation_id: str) -> dict[str, Any]:
        return self._post(f"/automations/{automation_id}/recommend", {})

    def compile(self, process_id: str, target: str) -> dict[str, Any]:
        return self._post(f"/processes/{process_id}/compile", {"target": target})

    def proofrun(self, process_id: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
        return self._post(f"/proofruns/process/{process_id}", {"cases": cases})

    def simulate(self, process_id: str, runs: int = 1000, **kwargs) -> dict[str, Any]:
        return self._post(f"/processes/{process_id}/simulate", {"runs": runs, **kwargs})

    def _get(self, path: str):
        response = self._client.get(path)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict):
        response = self._client.post(path, json=payload)
        response.raise_for_status()
        return response.json()
