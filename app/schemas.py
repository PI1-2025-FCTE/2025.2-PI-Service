from pydantic import BaseModel, Field
from typing import Optional


class TrajetoCreate(BaseModel):
    comandosEnviados: str = Field(..., min_length=1, description="Command string sent to ESP32")
    comandosExecutados: Optional[str] = Field(None, description="Commands actually executed")
    status: Optional[bool] = Field(True, description="True if completed successfully")
    tempo: Optional[int] = Field(None, ge=0, description="Execution time in milliseconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                { "comandosEnviados": "a1000da0001e" }
            ]
        }
    }

class TrajetoUpdate(BaseModel):
    status: Optional[bool] = None
    comandosExecutados: Optional[str] = None
    tempo: Optional[int] = None

class TrajetoResponse(BaseModel):
    idTrajeto: int
    comandosEnviados: str
    comandosExecutados: Optional[str]
    status: Optional[bool]
    tempo: Optional[int]

    model_config = {
        "from_attributes": True
    }