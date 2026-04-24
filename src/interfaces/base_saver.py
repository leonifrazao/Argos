from abc import ABC, abstractmethod
from pathlib import Path
from src.models import ComplianceResponse


class BaseSaver(ABC):
    @abstractmethod
    def save(self, data: list[ComplianceResponse], path: Path) -> None: ...
