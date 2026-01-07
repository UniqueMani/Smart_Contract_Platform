from datetime import datetime
from pydantic import BaseModel, Field

class QuantityCreate(BaseModel):
    contract_id: int
    period: str
    completion_ratio: float = Field(..., ge=0.0, le=1.0)
    completion_description: str = Field(..., min_length=1, description="完工情况描述（必填）")
    note: str | None = None
    seal_password: str | None = Field(None, description="签章密码（用于电子签章确认）")

class QuantityOut(BaseModel):
    id: int
    contract_id: int
    period: str
    completion_ratio: float
    completion_description: str
    note: str | None
    created_by: str
    created_at: datetime
    sealed: bool
    sealed_by: str | None
    sealed_at: datetime | None
    sealed_ip: str | None
