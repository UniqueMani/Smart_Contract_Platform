from datetime import datetime
from pydantic import BaseModel, Field

class QuantityCreate(BaseModel):
    contract_id: int
    period: str
    completion_ratio: float = Field(..., ge=0.0, le=1.0)
    note: str | None = None

class QuantityOut(BaseModel):
    id: int
    contract_id: int
    period: str
    completion_ratio: float
    note: str | None
    created_by: str
    created_at: datetime
