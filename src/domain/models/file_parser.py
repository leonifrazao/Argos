from pathlib import Path
from loguru import logger
from src.interfaces import BaseParser


class FileParser(BaseParser):
    def __init__(self) -> None:
        self._parsers: dict[str, BaseParser] = {}

    def register(self, extension: str, parser: BaseParser) -> None:
        """Registra um parser para uma extensão."""
        self._parsers[extension] = parser

    def parse(self, path: Path) -> str:
        """Delega o parsing pro parser correto baseado na extensão."""
        extension: str = path.suffix.lower()

        if extension not in self._parsers:
            raise ValueError(f"formato não suportado: {extension}")

        return self._parsers[extension].parse(path)