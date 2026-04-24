from pydantic import BaseModel


class ComplianceContext(BaseModel):
    empresa: str
    setor: str