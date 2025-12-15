from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.contract import ContractCreate, ContractOut, ContractUpdate
from app.models.contract import Contract
from app.crud.crud_contract import contract_create, contract_get, contract_list, contract_get_by_no, contract_update
from app.crud.crud_audit import audit_add
from app.services.rules import performance_bond, enforce_contract_price_equals_tender

router = APIRouter(prefix="/contracts", tags=["contracts"])

def can_view(u: CurrentUser, c: Contract) -> bool:
    if u.role in ("ADMIN", "AUDITOR", "OWNER_CONTRACT", "OWNER_FINANCE", "OWNER_LEGAL", "OWNER_LEADER", "SUPERVISOR"):
        return True
    if u.role == "CONTRACTOR":
        return u.company is None or c.contractor_org == u.company
    return False

@router.post("", response_model=ContractOut)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_CONTRACT", "ADMIN"))):
    if contract_get_by_no(db, payload.contract_no):
        raise HTTPException(400, "contract_no exists")
    enforce_contract_price_equals_tender(payload.tender_price, payload.contract_price)
    c = Contract(
        contract_no=payload.contract_no,
        contract_name=payload.contract_name,
        project_name=payload.project_name,
        owner_org=payload.owner_org,
        contractor_org=payload.contractor_org,
        tender_price=payload.tender_price,
        contract_price=payload.contract_price,
        performance_bond=performance_bond(payload.tender_price),
        approved_budget=payload.approved_budget,
        completion_ratio=0.0,
        paid_total=0.0,
        status="DRAFT",
        created_by=u.username,
        created_at=datetime.utcnow(),
    )
    c = contract_create(db, c)
    audit_add(db, u.username, "CREATE", "Contract", str(c.id), f"create contract {c.contract_no}")
    return ContractOut(**c.__dict__)

@router.get("", response_model=list[ContractOut])
def list_contracts(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = contract_list(db)
    res = []
    for c in items:
        if can_view(u, c):
            res.append(ContractOut(**c.__dict__))
    return res

@router.get("/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    if not can_view(u, c):
        raise HTTPException(403, "forbidden")
    return ContractOut(**c.__dict__)

@router.put("/{contract_id}", response_model=ContractOut)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_CONTRACT", "ADMIN"))):
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    if payload.contract_name is not None:
        c.contract_name = payload.contract_name
    if payload.project_name is not None:
        c.project_name = payload.project_name
    if payload.approved_budget is not None:
        c.approved_budget = payload.approved_budget
    c = contract_update(db, c)
    audit_add(db, u.username, "UPDATE", "Contract", str(c.id), "update contract")
    return ContractOut(**c.__dict__)

@router.post("/{contract_id}/submit")
def submit_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_CONTRACT", "ADMIN"))):
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    # demo 合规检查：核心字段已由规则强制；这里仅模拟“风险条款未整改禁止提交”
    # 规则：合同名称包含“风险”则禁止提交
    if "风险" in c.contract_name:
        raise HTTPException(400, "存在高风险条款（demo规则：合同名称含“风险”），请修改后再提交")
    c.status = "ACTIVE"
    contract_update(db, c)
    audit_add(db, u.username, "SUBMIT", "Contract", str(c.id), "submit contract -> ACTIVE")
    return {"ok": True, "status": c.status}
