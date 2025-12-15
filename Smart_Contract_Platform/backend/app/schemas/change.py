from datetime import datetime
from pydantic import BaseModel

class ChangeCreate(BaseModel):
    contract_id: int
    amount: float
    reason: str
    scope_desc: str
    schedule_impact_days: int = 0

class ChangeOut(BaseModel):
    id: int
    code: str
    contract_id: int
    amount: float
    reason: str
    scope_desc: str
    schedule_impact_days: int
    status: str
    created_by: str
    created_at: datetime

class ChangeTaskOut(BaseModel):
    id: int
    change_id: int
    step_order: int
    step_name: str
    assignee_role: str
    status: str
    comment: str | None = None
    action_at: datetime | None = None

class TaskAction(BaseModel):
    comment: str | None = None
