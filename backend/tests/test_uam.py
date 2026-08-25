import pytest
from pydantic import ValidationError

from app.core.uam import NodeKind, UAMEdge, UAMIntent, UAMNode, UAMProcess


def test_uam_validates_edges():
    with pytest.raises(ValidationError):
        UAMProcess(
            id="bad",
            name="Bad",
            intent=UAMIntent(objective="test"),
            nodes=[UAMNode(id="start", kind=NodeKind.START, name="Start")],
            edges=[UAMEdge(source="start", target="missing")],
        )


def test_uam_outgoing():
    process = UAMProcess(
        id="ok",
        name="OK",
        intent=UAMIntent(objective="test"),
        nodes=[
            UAMNode(id="start", kind=NodeKind.START, name="Start"),
            UAMNode(id="end", kind=NodeKind.END, name="End"),
        ],
        edges=[UAMEdge(source="start", target="end")],
    )
    assert process.outgoing("start")[0].target == "end"
