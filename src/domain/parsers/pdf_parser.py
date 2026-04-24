from pathlib import Path
from loguru import logger
from src.interfaces import BaseParser
import pdfplumber


class PdfParser(BaseParser):
    def parse(self, path: Path) -> str:
        """Extrai texto de um PDF."""
        with pdfplumber.open(path) as pdf:
            text: str = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

        logger.info(f"pdf parseado: {path.name}")
        return text