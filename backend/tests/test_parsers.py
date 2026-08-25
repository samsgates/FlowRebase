from pathlib import Path

from app.core.parsers.bpmn import BPMNParser
from app.core.parsers.python_source import PythonSourceParser
from app.core.parsers.uipath import UiPathParser
from app.core.uam import NodeKind


def test_uipath_parser_extracts_ui_and_apps():
    content = Path("../examples/invoice/Main.xaml").read_text()
    process = UiPathParser().parse(name="Invoice", content=content)
    assert process.source["type"] == "uipath"
    assert any(n.kind == NodeKind.UI_ACTION for n in process.nodes)
    assert "SAP" in process.applications


def test_bpmn_parser():
    xml = '''<?xml version="1.0"?>
    <definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
      <process id="p1">
        <startEvent id="start" />
        <serviceTask id="api" name="Call API" />
        <endEvent id="end" />
        <sequenceFlow id="f1" sourceRef="start" targetRef="api" />
        <sequenceFlow id="f2" sourceRef="api" targetRef="end" />
      </process>
    </definitions>'''
    process = BPMNParser().parse(name="BPMN", content=xml)
    assert len(process.nodes) == 3
    assert any(n.kind == NodeKind.API_CALL for n in process.nodes)


def test_python_parser():
    source = """
def run(amount):
    if amount > 10:
        return amount * 2
    return amount
"""
    process = PythonSourceParser().parse(name="Python", content=source)
    assert any(n.kind == NodeKind.DECISION for n in process.nodes)
