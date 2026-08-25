from __future__ import annotations

import json

import httpx

from ..config import get_settings
from ..core.uam import UAMProcess


class AIService:
    """Optional LLM augmentation. Core product logic never requires this service."""

    def __init__(self):
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.openai_api_key)

    async def explain_process(self, process: UAMProcess) -> dict:
        if not self.enabled:
            return {
                "enabled": False,
                "summary": f"{process.name} contains {len(process.nodes)} nodes across {len(process.applications)} identified applications.",
                "note": "Set OPENAI_API_KEY to enable optional model-assisted explanation.",
            }
        prompt = (
            "You are an enterprise automation architect. Summarize this UAM process. "
            "Do not invent facts. Separate evidence-backed facts from assumptions. Return JSON with "
            "summary, risks, modernization_opportunities. UAM:\n" + json.dumps(process.model_dump(mode="json"))[:50_000]
        )
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.settings.openai_model,
                    "input": prompt,
                    "text": {"format": {"type": "json_object"}},
                },
            )
            response.raise_for_status()
            body = response.json()
            # Responses API returns content blocks. Keep extraction tolerant to SDK/API changes.
            text = body.get("output_text")
            if not text:
                chunks = []
                for out in body.get("output", []):
                    for content in out.get("content", []):
                        if content.get("type") in {"output_text", "text"}:
                            chunks.append(content.get("text", ""))
                text = "".join(chunks)
            try:
                parsed = json.loads(text or "{}")
            except json.JSONDecodeError:
                parsed = {"summary": text or "Model returned no content"}
            return {"enabled": True, **parsed}
