from datetime import datetime
from pydantic import BaseModel

class PaymentCreate(BaseModel):
    contract_id: int
    amount: float
    purpose: str
    progress_desc: str
    period: str = ""

class PaymentOut(BaseModel):
    id: int
    code: str
    contract_id: int
    amount: float
    purpose: str
    progress_desc: str
    period: str
    status: str
    created_by: str
    created_at: datetime

class PaymentCalcOut(BaseModel):
    approved_budget: float
    completion_ratio: float
    paid_total: float
    payable_limit: float
    max_apply: float
