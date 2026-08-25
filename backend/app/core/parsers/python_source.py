from __future__ import annotations

import ast
import hashlib

from .base import SourceParser
from ..uam import Evidence, NodeKind, UAMEdge, UAMIntent, UAMNode, UAMProcess


class PythonSourceParser(SourceParser):
    source_type = "python"

    def parse(self, *, name: str, content: str, metadata: dict | None = None) -> UAMProcess:
        tree = ast.parse(content)
        nodes = [UAMNode(id="start", kind=NodeKind.START, name="Start")]
        edges: list[UAMEdge] = []
        evidence: list[Evidence] = []
        previous = "start"
        index = 0

        for item in ast.walk(tree):
            if not isinstance(item, (ast.Call, ast.If, ast.For, ast.While, ast.Assign, ast.Return)):
                continue
            index += 1
            node_id = f"py-{index}"
            kind = NodeKind.TASK
            label = item.__class__.__name__
            config = {"lineno": getattr(item, "lineno", None)}
            if isinstance(item, ast.Call):
                label = ast.unparse(item.func)
                lowered = label.lower()
                if any(k in lowered for k in ("requests.", "httpx.", "client.get", "client.post")):
                    kind = NodeKind.API_CALL
                elif any(k in lowered for k in ("execute", "cursor", "sql")):
                    kind = NodeKind.DATABASE
                else:
                    kind = NodeKind.SCRIPT
            elif isinstance(item, ast.If):
                kind = NodeKind.DECISION
                config["expression"] = ast.unparse(item.test)
                label = f"If {config['expression']}"
            elif isinstance(item, (ast.For, ast.While)):
                kind = NodeKind.LOOP
                label = ast.unparse(item).splitlines()[0].rstrip(":")
            elif isinstance(item, ast.Return):
                label = "Return"
                config["expression"] = ast.unparse(item.value) if item.value else None

            ev_id = f"ev-{node_id}"
            evidence.append(
                Evidence(
                    id=ev_id,
                    source_type="python",
                    source_ref=f"line:{getattr(item, 'lineno', 0)}",
                    excerpt=ast.get_source_segment(content, item),
                    confidence=1,
                )
            )
            nodes.append(UAMNode(id=node_id, kind=kind, name=label, config=config, evidence_refs=[ev_id]))
            edges.append(UAMEdge(source=previous, target=node_id))
            previous = node_id

        nodes.append(UAMNode(id="end", kind=NodeKind.END, name="End"))
        edges.append(UAMEdge(source=previous, target="end"))
        digest = hashlib.sha256(content.encode()).hexdigest()
        return UAMProcess(
            id=f"uam-{digest[:12]}",
            name=name,
            source={"type": "python", "sha256": digest, **(metadata or {})},
            intent=UAMIntent(objective=f"Modernize Python automation: {name}"),
            nodes=nodes,
            edges=edges,
            evidence=evidence,
            extensions={"parser": "flowrebase.python.v1"},
        )
