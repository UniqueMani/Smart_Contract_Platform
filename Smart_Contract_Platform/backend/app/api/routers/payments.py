from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentCalcOut
from app.models.payment import PaymentRequest
from app.crud.crud_payment import payment_create, payment_get, payment_list
from app.crud.crud_contract import contract_get, contract_update
from app.services.rules import calc_payment
from app.crud.crud_notification import notify_create
from app.crud.crud_audit import audit_add

router = APIRouter(prefix="/payments", tags=["payments"])

def gen_code(prefix: str) -> str:
    yyyy = datetime.utcnow().strftime("%Y")
    rnd = random.randint(1, 999)
    return f"{prefix}-{yyyy}-{rnd:03d}"

@router.post("", response_model=PaymentOut)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("CONTRACTOR", "ADMIN"))):
    c = contract_get(db, payload.contract_id)
    if not c:
        raise HTTPException(404, "contract not found")
    if u.role == "CONTRACTOR" and u.company and c.contractor_org != u.company:
        raise HTTPException(403, "forbidden")

    p = PaymentRequest(
        code=gen_code("ZF"),
        contract_id=payload.contract_id,
        amount=payload.amount,
        purpose=payload.purpose,
        progress_desc=payload.progress_desc,
        period=payload.period,
        status="SUBMITTED",
        created_by=u.username,
        created_at=datetime.utcnow(),
    )
    p = payment_create(db, p)
    notify_create(db, "owner_contract", "新的支付申请待审核", f"{p.code} 金额 {p.amount} 元")
    audit_add(db, u.username, "CREATE", "Payment", str(p.id), f"submit payment {p.code}")
    return PaymentOut(**p.__dict__)

@router.get("", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = payment_list(db)
    res=[]
    for p in items:
        c = contract_get(db, p.contract_id)
        if not c:
            continue
        if u.role in ("ADMIN","AUDITOR","OWNER_CONTRACT","OWNER_FINANCE","OWNER_LEGAL","OWNER_LEADER","SUPERVISOR"):
            res.append(PaymentOut(**p.__dict__))
        elif u.role == "CONTRACTOR":
            if u.company is None or c.contractor_org == u.company:
                res.append(PaymentOut(**p.__dict__))
    return res

@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    return PaymentOut(**p.__dict__)

@router.get("/{payment_id}/calc", response_model=PaymentCalcOut)
def get_calc(payment_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    c = contract_get(db, p.contract_id)
    calc = calc_payment(c.approved_budget, c.completion_ratio, c.paid_total)
    return PaymentCalcOut(
        approved_budget=c.approved_budget,
        completion_ratio=c.completion_ratio,
        paid_total=c.paid_total,
        payable_limit=calc.payable_limit,
        max_apply=calc.max_apply,
    )

@router.post("/{payment_id}/review/contract")
def contract_review(payment_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_CONTRACT","ADMIN"))):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    if p.status not in ("SUBMITTED","CONTRACT_REVIEW"):
        raise HTTPException(400, "invalid status")
    p.status = "FINANCE_REVIEW"
    db.add(p); db.commit(); db.refresh(p)
    notify_create(db, "owner_finance", "支付申请进入财务审核", f"{p.code} 金额 {p.amount} 元")
    audit_add(db, u.username, "REVIEW", "Payment", str(p.id), "contract review -> finance")
    return {"ok": True, "status": p.status}

@router.post("/{payment_id}/review/finance/approve")
def finance_approve(payment_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_FINANCE","ADMIN"))):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    if p.status not in ("FINANCE_REVIEW",):
        raise HTTPException(400, "invalid status")
    c = contract_get(db, p.contract_id)
    calc = calc_payment(c.approved_budget, c.completion_ratio, c.paid_total)

    if p.amount > calc.max_apply + 1e-6:
        p.status = "BLOCKED"
        db.add(p); db.commit(); db.refresh(p)
        over = round(p.amount - calc.max_apply, 2)
        msg = (f"申请金额超出可申请最大金额 {over} 元；"
               f"依据：批复概算={c.approved_budget}，完工比例={c.completion_ratio}，"
               f"可支付额度={calc.payable_limit}，已支付累计={c.paid_total}，"
               f"可申请最大金额={calc.max_apply}，申请金额={p.amount}")
        notify_create(db, "owner_contract", "超额支付预警单（demo）", f"{p.code}：{msg}")
        notify_create(db, p.created_by, "支付申请被拦截（超概算）", f"{p.code}：{msg}")
        audit_add(db, u.username, "BLOCK", "Payment", str(p.id), msg)
        return {"ok": False, "status": p.status, "reason": msg}

    # 通过 -> 视为已支付
    p.status = "PAID"
    c.paid_total = round(c.paid_total + p.amount, 2)
    contract_update(db, c)
    db.add(p); db.commit(); db.refresh(p)

    notify_create(db, p.created_by, "支付已完成", f"{p.code} 已支付 {p.amount} 元")
    audit_add(db, u.username, "PAY", "Payment", str(p.id), f"paid {p.amount}")
    return {"ok": True, "status": p.status}

@router.post("/{payment_id}/review/finance/reject")
def finance_reject(payment_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_FINANCE","ADMIN"))):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    p.status = "REJECTED"
    db.add(p); db.commit(); db.refresh(p)
    notify_create(db, p.created_by, "支付申请被驳回", f"{p.code} 已被驳回（demo）")
    audit_add(db, u.username, "REJECT", "Payment", str(p.id), "finance reject")
    return {"ok": True, "status": p.status}
