from .bpmn_target import BPMNTargetCompiler
from .power_automate import PowerAutomateDraftCompiler
from .python_target import PythonTargetCompiler

COMPILERS = {
    "python": PythonTargetCompiler(),
    "bpmn": BPMNTargetCompiler(),
    "power_automate": PowerAutomateDraftCompiler(),
}
