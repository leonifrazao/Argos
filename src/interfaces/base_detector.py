from abc import ABC, abstractmethod
from pathlib import Path


class BaseDetector(ABC):
    @abstractmethod
    def detect(self, path: Path): ...
