from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.contract import ContractCreate, ContractOut, ContractUpdate, ContractReject
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
    try:
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
            clauses=payload.clauses,
            start_date=payload.start_date,
            end_date=payload.end_date,
            completion_ratio=0.0,
            paid_total=0.0,
            status="DRAFT",
            created_by=u.username,
            created_at=datetime.utcnow(),
        )
        c = contract_create(db, c, commit=False)
        audit_add(db, u.username, "CREATE", "Contract", str(c.id), f"create contract {c.contract_no}", commit=False)
        db.commit()
        db.refresh(c)
        # 修复：直接访问属性而不是使用 __dict__
        return ContractOut(
            id=c.id,
            contract_no=c.contract_no,
            contract_name=c.contract_name,
            project_name=c.project_name,
            owner_org=c.owner_org,
            contractor_org=c.contractor_org,
            tender_price=c.tender_price,
            contract_price=c.contract_price,
            performance_bond=c.performance_bond,
            approved_budget=c.approved_budget,
            completion_ratio=c.completion_ratio,
            paid_total=c.paid_total,
            clauses=c.clauses,
            start_date=c.start_date,
            end_date=c.end_date,
            status=c.status,
            created_by=c.created_by,
            created_at=c.created_at,
        )
    except Exception as e:
        db.rollback()
        raise

@router.get("", response_model=list[ContractOut])
def list_contracts(
    search: str | None = None,
    contract_no: str | None = None,
    contract_name: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    u: CurrentUser = Depends(get_current_user)
):
    items = contract_list(db, search=search, contract_no=contract_no, contract_name=contract_name)
    res = []
    for c in items:
        if can_view(u, c):
            if status is None or c.status == status:
                # 修复：直接访问属性而不是使用 __dict__
                res.append(ContractOut(
                    id=c.id,
                    contract_no=c.contract_no,
                    contract_name=c.contract_name,
                    project_name=c.project_name,
                    owner_org=c.owner_org,
                    contractor_org=c.contractor_org,
                    tender_price=c.tender_price,
                    contract_price=c.contract_price,
                    performance_bond=c.performance_bond,
                    approved_budget=c.approved_budget,
                    completion_ratio=c.completion_ratio,
                    paid_total=c.paid_total,
                    clauses=c.clauses,
                    start_date=c.start_date,
                    end_date=c.end_date,
                    status=c.status,
                    created_by=c.created_by,
                    created_at=c.created_at,
                ))
    return res

@router.get("/pending/legal", response_model=list[ContractOut])
def get_pending_legal_review(db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_LEGAL", "ADMIN"))):
    """获取待法务审核的合同列表"""
    items = contract_list(db)
    # 修复：直接访问属性而不是使用 __dict__
    return [
        ContractOut(
            id=c.id,
            contract_no=c.contract_no,
            contract_name=c.contract_name,
            project_name=c.project_name,
            owner_org=c.owner_org,
            contractor_org=c.contractor_org,
            tender_price=c.tender_price,
            contract_price=c.contract_price,
            performance_bond=c.performance_bond,
            approved_budget=c.approved_budget,
            completion_ratio=c.completion_ratio,
            paid_total=c.paid_total,
            clauses=c.clauses,
            start_date=c.start_date,
            end_date=c.end_date,
            status=c.status,
            created_by=c.created_by,
            created_at=c.created_at,
        )
        for c in items if c.status == "APPROVING"
    ]

@router.get("/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    if not can_view(u, c):
        raise HTTPException(403, "forbidden")
    # 修复：直接访问属性而不是使用 __dict__
    return ContractOut(
        id=c.id,
        contract_no=c.contract_no,
        contract_name=c.contract_name,
        project_name=c.project_name,
        owner_org=c.owner_org,
        contractor_org=c.contractor_org,
        tender_price=c.tender_price,
        contract_price=c.contract_price,
        performance_bond=c.performance_bond,
        approved_budget=c.approved_budget,
        completion_ratio=c.completion_ratio,
        paid_total=c.paid_total,
        clauses=c.clauses,
        start_date=c.start_date,
        end_date=c.end_date,
        status=c.status,
        created_by=c.created_by,
        created_at=c.created_at,
    )

@router.put("/{contract_id}", response_model=ContractOut)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_CONTRACT", "ADMIN"))):
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    try:
        if payload.contract_name is not None:
            c.contract_name = payload.contract_name
        if payload.project_name is not None:
            c.project_name = payload.project_name
        if payload.approved_budget is not None:
            c.approved_budget = payload.approved_budget
        if payload.clauses is not None:
            c.clauses = payload.clauses
        if payload.start_date is not None:
            c.start_date = payload.start_date
        if payload.end_date is not None:
            c.end_date = payload.end_date
        c = contract_update(db, c, commit=False)
        audit_add(db, u.username, "UPDATE", "Contract", str(c.id), "update contract", commit=False)
        db.commit()
        db.refresh(c)
        # 修复：直接访问属性而不是使用 __dict__
        return ContractOut(
            id=c.id,
            contract_no=c.contract_no,
            contract_name=c.contract_name,
            project_name=c.project_name,
            owner_org=c.owner_org,
            contractor_org=c.contractor_org,
            tender_price=c.tender_price,
            contract_price=c.contract_price,
            performance_bond=c.performance_bond,
            approved_budget=c.approved_budget,
            completion_ratio=c.completion_ratio,
            paid_total=c.paid_total,
            clauses=c.clauses,
            start_date=c.start_date,
            end_date=c.end_date,
            status=c.status,
            created_by=c.created_by,
            created_at=c.created_at,
        )
    except Exception as e:
        db.rollback()
        raise

@router.post("/{contract_id}/submit")
def submit_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_CONTRACT", "ADMIN"))):
    """合同管理员提交合同给法务审核"""
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    if c.status != "DRAFT":
        raise HTTPException(400, "只能提交草稿状态的合同")
    # demo 合规检查：核心字段已由规则强制；这里仅模拟"风险条款未整改禁止提交"
    # 规则：合同名称包含"风险"则禁止提交
    if "风险" in c.contract_name:
        raise HTTPException(400, "存在高风险条款，请修改后再提交")
    try:
        from app.crud.crud_notification import notify_create
        c.status = "APPROVING"  # 提交后进入审核状态，等待法务审核
        contract_update(db, c, commit=False)
        notify_create(db, to_username="owner_legal", title="新的合同待法务审核", content=f"{c.contract_no} {c.contract_name} 待审核", commit=False)
        audit_add(db, u.username, "SUBMIT", "Contract", str(c.id), "submit contract -> APPROVING (等待法务审核)", commit=False)
        db.commit()
        db.refresh(c)
        return {"ok": True, "status": c.status}
    except Exception as e:
        db.rollback()
        raise

@router.post("/{contract_id}/review/legal")
def legal_review_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_LEGAL", "ADMIN"))):
    """法务审核合同，审核通过后合同变为 ACTIVE"""
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    if c.status != "APPROVING":
        raise HTTPException(400, "只能审核 APPROVING 状态的合同")
    try:
        from app.crud.crud_notification import notify_create
        c.status = "ACTIVE"
        contract_update(db, c, commit=False)
        notify_create(db, to_username=c.created_by, title="合同审核通过", content=f"{c.contract_no} {c.contract_name} 已通过法务审核，合同已生效", commit=False)
        audit_add(db, u.username, "APPROVE", "Contract", str(c.id), "legal review -> ACTIVE", commit=False)
        db.commit()
        db.refresh(c)
        return {"ok": True, "status": c.status}
    except Exception as e:
        db.rollback()
        raise

@router.post("/{contract_id}/reject/legal")
def legal_reject_contract(contract_id: int, payload: ContractReject, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_LEGAL", "ADMIN"))):
    """法务驳回合同，合同退回为 DRAFT 状态"""
    c = contract_get(db, contract_id)
    if not c:
        raise HTTPException(404, "not found")
    if c.status != "APPROVING":
        raise HTTPException(400, "只能驳回 APPROVING 状态的合同")
    try:
        from app.crud.crud_notification import notify_create
        reject_reason = payload.reason or "法务审核未通过"
        c.status = "DRAFT"
        contract_update(db, c, commit=False)
        notify_create(db, to_username=c.created_by, title="合同被驳回", content=f"{c.contract_no} {c.contract_name} 被法务驳回，原因：{reject_reason}", commit=False)
        audit_add(db, u.username, "REJECT", "Contract", str(c.id), f"legal reject: {reject_reason}", commit=False)
        db.commit()
        db.refresh(c)
        return {"ok": True, "status": c.status}
    except Exception as e:
        db.rollback()
        raise
