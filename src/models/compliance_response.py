from pydantic import BaseModel
from typing import Literal


class ComplianceResponse(BaseModel):
    pessoa_id: int
    bbox: dict[str, int]
    status: Literal["Conforme", "Não conforme", "Indeterminado"]
    justificativa: str