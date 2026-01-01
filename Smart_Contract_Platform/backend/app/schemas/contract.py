from datetime import datetime
from pydantic import BaseModel, Field

class ContractCreate(BaseModel):
    contract_no: str = Field(..., examples=["HT-2025-001"])
    contract_name: str
    project_name: str
    owner_org: str
    contractor_org: str
    tender_price: float
    contract_price: float
    approved_budget: float
    clauses: str | None = None  # 合同条款
    start_date: datetime | None = None  # 合同开始日期
    end_date: datetime | None = None  # 合同结束日期

class ContractOut(BaseModel):
    id: int
    contract_no: str
    contract_name: str
    project_name: str
    owner_org: str
    contractor_org: str
    tender_price: float
    contract_price: float
    performance_bond: float
    approved_budget: float
    completion_ratio: float
    paid_total: float
    clauses: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str
    created_by: str
    created_at: datetime

class ContractUpdate(BaseModel):
    contract_name: str | None = None
    project_name: str | None = None
    approved_budget: float | None = None
    clauses: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
