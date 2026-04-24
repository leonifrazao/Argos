from pathlib import Path
from loguru import logger
from src.interfaces import BaseSaver
from src.models import ComplianceResponse
import json


class JsonSaver(BaseSaver):
    def save(self, data: list[ComplianceResponse], path: Path) -> None:
        """Salva a lista de resultados em um arquivo JSON."""
        
        # Pydantic 2.0+ facilita exportar models como dicts
        dict_data = [item.model_dump() for item in data]
        
        # Garante que o diretório exista
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dict_data, f, ensure_ascii=False, indent=4)
            
        logger.info(f"resultados salvos com sucesso em: {path}")
