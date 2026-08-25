from abc import ABC, abstractmethod

from ..uam import UAMProcess


class SourceParser(ABC):
    source_type: str

    @abstractmethod
    def parse(self, *, name: str, content: str, metadata: dict | None = None) -> UAMProcess:
        raise NotImplementedError
