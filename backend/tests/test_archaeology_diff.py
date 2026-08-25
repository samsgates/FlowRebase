from copy import deepcopy

from app.core.archaeology import ProcessArchaeology
from app.core.demo import demo_uam
from app.core.diff import diff_uam
from app.core.uam import UAMProcess


def test_archaeology_detects_policy_conflict():
    result = ProcessArchaeology().analyze(
        demo_uam(),
        [{"name": "new-policy", "content": "Invoices above $7,500 require manager approval."}],
    )
    assert result["status"] == "conflict"
    assert result["conflicts"][0]["key"] == "approval_threshold"


def test_uam_diff_detects_node_change():
    before = demo_uam()
    data = deepcopy(before.model_dump(mode="json"))
    data["version"] = "1.1.0"
    data["nodes"][1]["name"] = "Extract invoice document"
    after = UAMProcess.model_validate(data)
    diff = diff_uam(before, after)
    assert diff["has_changes"] is True
    assert diff["nodes"]["changed"][0]["id"] == "extract"
