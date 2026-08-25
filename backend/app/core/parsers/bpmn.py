from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET

from .base import SourceParser
from ..uam import Determinism, Evidence, NodeKind, UAMEdge, UAMIntent, UAMNode, UAMProcess


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


class BPMNParser(SourceParser):
    source_type = "bpmn"

    TYPES = {
        "startEvent": NodeKind.START,
        "endEvent": NodeKind.END,
        "task": NodeKind.TASK,
        "serviceTask": NodeKind.API_CALL,
        "userTask": NodeKind.HUMAN,
        "scriptTask": NodeKind.SCRIPT,
        "manualTask": NodeKind.HUMAN,
        "businessRuleTask": NodeKind.POLICY,
        "exclusiveGateway": NodeKind.DECISION,
        "parallelGateway": NodeKind.PARALLEL,
        "eventBasedGateway": NodeKind.DECISION,
        "subProcess": NodeKind.SUBPROCESS,
        "intermediateCatchEvent": NodeKind.EVENT,
        "intermediateThrowEvent": NodeKind.EVENT,
    }

    def parse(self, *, name: str, content: str, metadata: dict | None = None) -> UAMProcess:
        root = ET.fromstring(content)
        nodes: list[UAMNode] = []
        edges: list[UAMEdge] = []
        evidence: list[Evidence] = []

        for elem in root.iter():
            tag = local(elem.tag)
            if tag not in self.TYPES:
                continue
            node_id = elem.attrib.get("id") or f"node-{len(nodes)+1}"
            node_name = elem.attrib.get("name") or tag
            kind = self.TYPES[tag]
            determinism = (
                Determinism.HUMAN_ACCOUNTABLE if kind == NodeKind.HUMAN else Determinism.DETERMINISTIC
            )
            ev_id = f"ev-{node_id}"
            evidence.append(Evidence(id=ev_id, source_type="bpmn", source_ref=node_id, confidence=1))
            nodes.append(
                UAMNode(
                    id=node_id,
                    kind=kind,
                    name=node_name,
                    determinism=determinism,
                    evidence_refs=[ev_id],
                    config={"bpmn_type": tag},
                )
            )

        for elem in root.iter():
            if local(elem.tag) != "sequenceFlow":
                continue
            source, target = elem.attrib.get("sourceRef"), elem.attrib.get("targetRef")
            if source and target:
                condition = None
                for child in elem:
                    if local(child.tag) == "conditionExpression":
                        condition = (child.text or "").strip()
                edges.append(UAMEdge(source=source, target=target, label=elem.attrib.get("name"), condition=condition))

        if not nodes:
            raise ValueError("No BPMN process nodes found")
        digest = hashlib.sha256(content.encode()).hexdigest()
        return UAMProcess(
            id=f"uam-{digest[:12]}",
            name=name,
            source={"type": "bpmn", "sha256": digest, **(metadata or {})},
            intent=UAMIntent(objective=f"Execute business process: {name}"),
            nodes=nodes,
            edges=edges,
            evidence=evidence,
            extensions={"parser": "flowrebase.bpmn.v1"},
        )
