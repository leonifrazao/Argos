from loguru import logger
from src.interfaces import BaseAnalyzer
from src.models import PersonResponse, ComplianceResponse


class AnalyzerRegistry(BaseAnalyzer):
    def __init__(self) -> None:
        self._analyzers: dict[str, BaseAnalyzer] = {}

    def register(self, provider: str, analyzer: BaseAnalyzer) -> None:
        """Registra um analyzer para um provider."""
        self._analyzers[provider] = analyzer

    def analyze(self, provider: str, persons: list[PersonResponse], rules: list[str]) -> list[ComplianceResponse]:
        """Delega a análise em lote pro analyzer correto baseado no provider."""
        if provider not in self._analyzers:
            raise ValueError(f"provider não suportado: {provider}")

        return self._analyzers[provider].analyze(persons, rules)