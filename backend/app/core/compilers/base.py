from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..uam import UAMProcess


@dataclass
class CompiledArtifact:
    target: str
    filename: str
    media_type: str
    content: str
    warnings: list[str] = field(default_factory=list)


class TargetCompiler(ABC):
    target: str

    @abstractmethod
    def compile(self, process: UAMProcess) -> CompiledArtifact:
        raise NotImplementedError
