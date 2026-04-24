import yaml
import os
from pathlib import Path
from src.models import AppConfig
from dotenv import load_dotenv
from loguru import logger


class ConfigLoader:
    @staticmethod
    def load(config_path: str = "config.yaml") -> AppConfig:
        """Carrega e valida o YAML usando os modelos do Pydantic."""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")

        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        config = AppConfig(**data)
        
        load_dotenv()
        if not config.gemini.api_key:
            config.gemini.api_key = os.environ.get("GEMINI_API_KEY")
            
        return config
