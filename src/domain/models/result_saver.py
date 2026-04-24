from pathlib import Path
from loguru import logger
from src.interfaces import BaseSaver
from src.models import ComplianceResponse


class ResultSaver(BaseSaver):
    def __init__(self) -> None:
        self._savers: dict[str, BaseSaver] = {}

    def register(self, extension: str, saver: BaseSaver) -> None:
        """Registra um saver para uma extensão."""
        self._savers[extension] = saver

    def save(self, data: list[ComplianceResponse], path: Path) -> None:
        """Delega o salvamento pro saver correto baseado na extensão."""
        extension: str = path.suffix.lower()

        if extension not in self._savers:
            raise ValueError(f"formato não suportado para salvamento: {extension}")

        self._savers[extension].save(data, path)
