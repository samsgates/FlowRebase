from .bpmn import BPMNParser
from .python_source import PythonSourceParser
from .uipath import UiPathParser

PARSERS = {
    "uipath": UiPathParser(),
    "bpmn": BPMNParser(),
    "python": PythonSourceParser(),
}
