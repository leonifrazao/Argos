from pathlib import Path
from loguru import logger
from src.interfaces import BaseParser
from docx import Document


class DocxParser(BaseParser):
    def parse(self, path: Path) -> str:
        """Extrai texto de um DOCX."""
        doc: Document = Document(str(path))
        text: str = "\n".join(p.text for p in doc.paragraphs if p.text)

        logger.info(f"docx parseado: {path.name}")
        return text