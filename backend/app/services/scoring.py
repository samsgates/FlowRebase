from __future__ import annotations

from ..core.uam import NodeKind, UAMProcess


def score_process(process: UAMProcess, metadata: dict | None = None) -> tuple[float, float]:
    metadata = metadata or {}
    count = max(1, len(process.nodes))
    ui = sum(1 for n in process.nodes if n.kind == NodeKind.UI_ACTION)
    human = sum(1 for n in process.nodes if n.kind in {NodeKind.HUMAN, NodeKind.APPROVAL})
    undocumented = sum(1 for n in process.nodes if not n.evidence_refs)
    shared_credentials = sum(1 for c in process.credentials if c.get("shared"))
    observed_failure_rate = float(metadata.get("failure_rate", 0.05))

    risk = 15 + ui / count * 35 + human / count * 8 + shared_credentials * 12 + observed_failure_rate * 100 * 0.35
    health = 100 - risk - undocumented / count * 15
    return round(max(0, min(100, health)), 1), round(max(0, min(100, risk)), 1)
