from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Iterable

from .uam import NodeKind, UAMProcess


@dataclass
class ArchaeologyFact:
    key: str
    value: str | float | bool
    statement: str
    source_ref: str
    confidence: float


class ProcessArchaeology:
    """Evidence-first deterministic archaeology baseline.

    This engine intentionally extracts only explicit policy-like statements and source decision
    thresholds. Optional AI can enrich these candidates, but conflicts are computed from explicit
    facts so a model cannot silently overwrite business controls.
    """

    MONEY_THRESHOLD = re.compile(
        r"(?:above|over|greater than|exceed(?:s|ing)?)\s*\$?\s*([\d,]+(?:\.\d+)?)",
        re.IGNORECASE,
    )
    APPROVAL = re.compile(r"\b(?:approval|approve|approved)\b", re.IGNORECASE)
    RETENTION = re.compile(r"(?:retain|retention|kept|keep).*?(\d+)\s+years?", re.IGNORECASE)
    OBLIGATION = re.compile(r"\b(must|shall|required|requires|prohibited|forbidden|may not)\b", re.IGNORECASE)

    def analyze(self, process: UAMProcess, documents: Iterable[dict]) -> dict:
        facts: list[ArchaeologyFact] = []
        facts.extend(self._source_facts(process))
        for document in documents:
            facts.extend(self._document_facts(document))
        conflicts = self._conflicts(facts)
        return {
            "facts": [asdict(f) for f in facts],
            "conflicts": conflicts,
            "status": "conflict" if conflicts else "consistent",
            "evidence_count": len(facts),
        }

    def _source_facts(self, process: UAMProcess) -> list[ArchaeologyFact]:
        facts: list[ArchaeologyFact] = []
        for node in process.nodes:
            if node.kind != NodeKind.DECISION:
                continue
            expression = str(node.config.get("expression", ""))
            match = re.search(r"(?:amount|value|total)\s*>?=?\s*([\d,.]+)", expression, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(",", ""))
                facts.append(
                    ArchaeologyFact(
                        key="approval_threshold" if "amount" in expression.lower() else "decision_threshold",
                        value=value,
                        statement=expression,
                        source_ref=f"uam-node:{node.id}",
                        confidence=0.99,
                    )
                )
        return facts

    def _document_facts(self, document: dict) -> list[ArchaeologyFact]:
        name = str(document.get("name", "document"))
        text = str(document.get("content", ""))
        facts: list[ArchaeologyFact] = []
        for line_number, line in enumerate(text.splitlines(), 1):
            sentence = line.strip()
            if not sentence:
                continue
            money = self.MONEY_THRESHOLD.search(sentence)
            if money and self.APPROVAL.search(sentence):
                facts.append(
                    ArchaeologyFact(
                        key="approval_threshold",
                        value=float(money.group(1).replace(",", "")),
                        statement=sentence,
                        source_ref=f"{name}:line:{line_number}",
                        confidence=0.96,
                    )
                )
            retention = self.RETENTION.search(sentence)
            if retention:
                facts.append(
                    ArchaeologyFact(
                        key="retention_years",
                        value=float(retention.group(1)),
                        statement=sentence,
                        source_ref=f"{name}:line:{line_number}",
                        confidence=0.94,
                    )
                )
            if self.OBLIGATION.search(sentence) and not money and not retention:
                facts.append(
                    ArchaeologyFact(
                        key=f"obligation:{line_number}",
                        value=True,
                        statement=sentence,
                        source_ref=f"{name}:line:{line_number}",
                        confidence=0.90,
                    )
                )
        return facts

    @staticmethod
    def _conflicts(facts: list[ArchaeologyFact]) -> list[dict]:
        grouped: dict[str, list[ArchaeologyFact]] = {}
        for fact in facts:
            if fact.key.startswith("obligation:"):
                continue
            grouped.setdefault(fact.key, []).append(fact)
        conflicts: list[dict] = []
        for key, candidates in grouped.items():
            values = {str(c.value) for c in candidates}
            if len(values) > 1:
                conflicts.append(
                    {
                        "key": key,
                        "values": sorted(values),
                        "evidence": [asdict(c) for c in candidates],
                        "requires_review": True,
                    }
                )
        return conflicts
