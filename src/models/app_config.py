from pydantic import BaseModel


class GeminiConfig(BaseModel):
    model: str
    api_key: str | None = None


class YoloConfig(BaseModel):
    model_path: str
    threshold: float


class ChromaConfig(BaseModel):
    db_path: str
    embedder_model: str
    top_k: int


class DatasetConfig(BaseModel):
    path: str


class OutputConfig(BaseModel):
    results_path: str


class AppConfig(BaseModel):
    gemini: GeminiConfig
    yolo: YoloConfig
    chroma: ChromaConfig
    dataset: DatasetConfig
    output: OutputConfig
