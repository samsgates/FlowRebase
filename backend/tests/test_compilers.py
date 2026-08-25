import json

from app.core.compilers import COMPILERS
from app.core.demo import demo_uam


def test_compilers_emit_artifacts():
    process = demo_uam()
    py = COMPILERS["python"].compile(process)
    assert "async def vendor_invoice_processing" in py.content
    bpmn = COMPILERS["bpmn"].compile(process)
    assert "process" in bpmn.content
    draft = COMPILERS["power_automate"].compile(process)
    parsed = json.loads(draft.content)
    assert parsed["sourceUamId"] == process.id
    assert draft.warnings
