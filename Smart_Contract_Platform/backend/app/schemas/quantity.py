from datetime import datetime
from pydantic import BaseModel, Field

class QuantityCreate(BaseModel):
    contract_id: int
    period: str
    completion_ratio: float = Field(..., ge=0.0, le=1.0)
    note: str = Field(..., description="描述内容（必填）")

class QuantityOut(BaseModel):
    id: int
    contract_id: int
    period: str
    completion_ratio: float
    note: str
    created_by: str
    created_at: datetime
