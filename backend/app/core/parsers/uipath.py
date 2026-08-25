from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET

from .base import SourceParser
from ..uam import Determinism, Evidence, NodeKind, UAMEdge, UAMIntent, UAMNode, UAMProcess


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].rsplit(":", 1)[-1]


def _slug(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return clean[:50] or "activity"


class UiPathParser(SourceParser):
    source_type = "uipath"

    def parse(self, *, name: str, content: str, metadata: dict | None = None) -> UAMProcess:
        root = ET.fromstring(content)
        nodes: list[UAMNode] = [UAMNode(id="start", kind=NodeKind.START, name="Start")]
        edges: list[UAMEdge] = []
        evidence: list[Evidence] = []
        apps: set[str] = set()
        previous = "start"
        index = 0

        ignored = {
            "Activity", "Members", "TextExpression.ReferencesForImplementation",
            "TextExpression.NamespacesForImplementation", "VisualBasic.Settings",
            "Sequence.Variables", "Variable", "Literal", "Reference",
        }

        for elem in root.iter():
            tag = _local(elem.tag)
            if tag in ignored or tag.endswith(".Arguments") or tag.endswith(".Variables"):
                continue
            if elem is root and tag in {"Activity", "Sequence"}:
                continue
            display = elem.attrib.get("DisplayName") or elem.attrib.get("Name") or tag
            if not display or display.startswith("sap2010:"):
                continue

            index += 1
            node_id = f"n{index}-{_slug(display)}"
            lower = f"{tag} {display}".lower()
            kind = NodeKind.ROBOT_ACTION
            determinism = Determinism.DETERMINISTIC
            config = {"source_activity": tag, "attributes": dict(elem.attrib)}

            if tag in {"If", "Switch", "FlowDecision"}:
                kind = NodeKind.DECISION
                condition = elem.attrib.get("Condition") or elem.attrib.get("Expression")
                if condition:
                    config["expression"] = condition.strip("[]")
            elif "assign" in lower:
                kind = NodeKind.TASK
            elif "invoke" in lower or "http" in lower:
                kind = NodeKind.API_CALL
            elif any(x in lower for x in ("click", "type into", "selector", "browser", "window")):
                kind = NodeKind.UI_ACTION
            elif any(x in lower for x in ("read range", "excel", "workbook")):
                kind = NodeKind.DOCUMENT
                apps.add("Microsoft Excel")
            elif any(x in lower for x in ("message box", "input dialog")):
                kind = NodeKind.HUMAN
                determinism = Determinism.HUMAN_ACCOUNTABLE
            elif "delay" in lower:
                kind = NodeKind.WAIT

            app = None
            if "sap" in lower:
                app = "SAP"
                apps.add(app)
            elif "outlook" in lower:
                app = "Microsoft Outlook"
                apps.add(app)
            elif "salesforce" in lower:
                app = "Salesforce"
                apps.add(app)

            ev_id = f"ev-{index}"
            evidence.append(
                Evidence(
                    id=ev_id,
                    source_type="uipath-xaml",
                    source_ref=f"activity:{display}",
                    excerpt=ET.tostring(elem, encoding="unicode")[:500],
                    confidence=0.98,
                )
            )
            nodes.append(
                UAMNode(
                    id=node_id,
                    kind=kind,
                    name=display,
                    determinism=determinism,
                    config=config,
                    application=app,
                    evidence_refs=[ev_id],
                )
            )
            edges.append(UAMEdge(source=previous, target=node_id))
            previous = node_id

        nodes.append(UAMNode(id="end", kind=NodeKind.END, name="End"))
        edges.append(UAMEdge(source=previous, target="end"))

        digest = hashlib.sha256(content.encode()).hexdigest()[:12]
        return UAMProcess(
            id=f"uam-{digest}",
            name=name,
            source={"type": "uipath", "sha256": hashlib.sha256(content.encode()).hexdigest(), **(metadata or {})},
            intent=UAMIntent(objective=f"Modernize automation: {name}"),
            nodes=nodes,
            edges=edges,
            applications=sorted(apps),
            evidence=evidence,
            extensions={"parser": "flowrebase.uipath.v1"},
        )
