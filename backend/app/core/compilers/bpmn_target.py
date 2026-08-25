from __future__ import annotations

import xml.etree.ElementTree as ET

from .base import CompiledArtifact, TargetCompiler
from ..uam import NodeKind, UAMProcess


class BPMNTargetCompiler(TargetCompiler):
    target = "bpmn"

    MAP = {
        NodeKind.START: "startEvent",
        NodeKind.END: "endEvent",
        NodeKind.TASK: "task",
        NodeKind.API_CALL: "serviceTask",
        NodeKind.DATABASE: "serviceTask",
        NodeKind.SCRIPT: "scriptTask",
        NodeKind.HUMAN: "userTask",
        NodeKind.APPROVAL: "userTask",
        NodeKind.DECISION: "exclusiveGateway",
        NodeKind.PARALLEL: "parallelGateway",
        NodeKind.SUBPROCESS: "subProcess",
        NodeKind.POLICY: "businessRuleTask",
        NodeKind.AGENT: "serviceTask",
        NodeKind.UI_ACTION: "serviceTask",
        NodeKind.ROBOT_ACTION: "serviceTask",
    }

    def compile(self, process: UAMProcess) -> CompiledArtifact:
        ns = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        ET.register_namespace("bpmn", ns)
        defs = ET.Element(f"{{{ns}}}definitions", attrib={"id": f"Definitions_{process.id}", "targetNamespace": "https://flowrebase.dev/uam"})
        proc = ET.SubElement(defs, f"{{{ns}}}process", attrib={"id": process.id, "name": process.name, "isExecutable": "true"})
        warnings: list[str] = []
        for node in process.nodes:
            tag = self.MAP.get(node.kind, "task")
            attrs = {"id": node.id, "name": node.name}
            if node.kind in {NodeKind.UI_ACTION, NodeKind.ROBOT_ACTION, NodeKind.AGENT}:
                attrs["implementation"] = f"flowrebase:{node.kind.value}"
                warnings.append(f"{node.name}: emitted as serviceTask with FlowRebase implementation extension.")
            ET.SubElement(proc, f"{{{ns}}}{tag}", attrib=attrs)
        for i, edge in enumerate(process.edges, 1):
            attrs = {"id": f"Flow_{i}", "sourceRef": edge.source, "targetRef": edge.target}
            if edge.label:
                attrs["name"] = edge.label
            flow = ET.SubElement(proc, f"{{{ns}}}sequenceFlow", attrib=attrs)
            if edge.condition:
                condition = ET.SubElement(flow, f"{{{ns}}}conditionExpression")
                condition.text = edge.condition
        content = ET.tostring(defs, encoding="unicode", xml_declaration=True)
        return CompiledArtifact(self.target, f"{process.id}.bpmn", "application/xml", content, warnings)
