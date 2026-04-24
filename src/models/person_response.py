from pydantic import BaseModel, confloat, Field
from datetime import datetime
from typing import Any
import numpy as np


class PersonResponse(BaseModel):
    id: int
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: confloat(ge=0.0, le=1.0)
    box: dict[str, int]  # {'x_min': 0, 'y_min': 0, 'x_max': 0, 'y_max': 0}
    crop: Any  # numpy array do recorte

    model_config = {"arbitrary_types_allowed": True}