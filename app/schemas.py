from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class TrajetoCreate(BaseModel):
    comandosEnviados: str = Field(..., min_length=1, description="Command string sent to ESP32")
    comandosExecutados: Optional[str] = Field(None, description="Commands actually executed")
    status: bool = Field(True, description="True if completed successfully")
    tempo: int = Field(..., ge=0, description="Execution time in seconds")
    trajectory_data: Optional[Dict[str, Any]] = Field(None, description="Trajectory points and metadata")
    distance_traveled: Optional[float] = Field(None, ge=0, description="Total distance in cm")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "comandosEnviados": "a1000da0001e",
                    "comandosExecutados": "a1000da0001e",
                    "status": True,
                    "tempo": 42
                }
            ]
        }
    }


class TrajetoResponse(BaseModel):
    idTrajeto: int
    timestamp: datetime
    comandosEnviados: str
    comandosExecutados: Optional[str]
    status: bool
    tempo: int

    model_config = {
        "from_attributes": True
    }