from app.core.advisor import Disposition, ModernizationAdvisor
from app.core.uam import NodeKind, UAMEdge, UAMIntent, UAMNode, UAMProcess


def test_advisor_detects_ui_heavy_process():
    nodes = [UAMNode(id="start", kind=NodeKind.START, name="Start")]
    for i in range(5):
        nodes.append(UAMNode(id=f"ui{i}", kind=NodeKind.UI_ACTION, name=f"Click {i}"))
    nodes.append(UAMNode(id="end", kind=NodeKind.END, name="End"))
    edges = [UAMEdge(source=nodes[i].id, target=nodes[i + 1].id) for i in range(len(nodes) - 1)]
    process = UAMProcess(id="p", name="UI", intent=UAMIntent(objective="test"), nodes=nodes, edges=edges)
    advice = ModernizationAdvisor().recommend(process)
    assert advice.disposition == Disposition.API_FY
    assert advice.confidence > 0.8
