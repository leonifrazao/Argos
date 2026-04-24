from abc import ABC, abstractmethod
from src.models import PersonResponse, ComplianceResponse


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, persons: list[PersonResponse], rules: list[str]) -> list[ComplianceResponse]: ...