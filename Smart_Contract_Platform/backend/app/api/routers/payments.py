from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
import time

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentCalcOut, PaymentReject
from app.models.payment import PaymentRequest
from app.crud.crud_payment import payment_create, payment_get, payment_list
from app.crud.crud_contract import contract_get, contract_update
from app.services.rules import calc_payment
from app.crud.crud_notification import notify_create
from app.crud.crud_audit import audit_add

router = APIRouter(prefix="/payments", tags=["payments"])

def to_payment_out(p: PaymentRequest) -> PaymentOut:
    """将 SQLAlchemy 模型转换为 Pydantic 模型"""
    # 直接访问属性，避免 __dict__ 可能为空的问题
    return PaymentOut(
        id=p.id,
        code=p.code,
        contract_id=p.contract_id,
        amount=p.amount,
        purpose=p.purpose,
        progress_desc=p.progress_desc,
        period=p.period,
        status=p.status,
        is_blocked=p.is_blocked,
        reject_reason=p.reject_reason,
        created_by=p.created_by,
        created_at=p.created_at,
    )

def gen_code(prefix: str, db: Session) -> str:
    """生成唯一的支付单号，如果重复则重试"""
    yyyy = datetime.utcnow().strftime("%Y")
    max_attempts = 10
    for _ in range(max_attempts):
        rnd = random.randint(1, 999)
        code = f"{prefix}-{yyyy}-{rnd:03d}"
        # 检查是否已存在
        existing = db.query(PaymentRequest).filter(PaymentRequest.code == code).first()
        if not existing:
            return code
    # 如果10次都重复（极不可能），使用时间戳
    return f"{prefix}-{yyyy}-{int(time.time()) % 10000:04d}"

@router.post("", response_model=PaymentOut)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("CONTRACTOR", "ADMIN"))):
    # 验证必填字段
    if not payload.contract_id:
        raise HTTPException(status_code=400, detail="合同ID不能为空")
    if not payload.amount or payload.amount <= 0:
        raise HTTPException(status_code=400, detail="申请金额必须大于0")
    if not payload.purpose or not payload.purpose.strip():
        raise HTTPException(status_code=400, detail="支付事由不能为空")
    
    c = contract_get(db, payload.contract_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"合同不存在 (ID: {payload.contract_id})")
    if u.role == "CONTRACTOR" and u.company and c.contractor_org != u.company:
        raise HTTPException(status_code=403, detail="无权操作此合同的支付申请")

    try:
        p = PaymentRequest(
            code=gen_code("ZF", db),
            contract_id=payload.contract_id,
            amount=payload.amount,
            purpose=payload.purpose,
            progress_desc=payload.progress_desc or "",
            period=payload.period or "",
            status="FINANCE_REVIEW",  # 直接进入财务审核，不再经过合同审核
            created_by=u.username,
            created_at=datetime.utcnow(),
        )
        p = payment_create(db, p)
        notify_create(db, "owner_finance", "新的支付申请待财务审核", f"{p.code} 金额 {p.amount} 元")
        audit_add(db, u.username, "CREATE", "Payment", str(p.id), f"submit payment {p.code} -> FINANCE_REVIEW")
        # 确保对象是最新的（因为 notify_create 和 audit_add 可能提交了事务）
        db.refresh(p)
        return to_payment_out(p)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # 返回详细的错误信息
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg or "unique constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="支付单号已存在，请稍后重试")
        elif "FOREIGN KEY constraint failed" in error_msg or "foreign key constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="合同ID无效")
        elif "NOT NULL constraint failed" in error_msg or "not null constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="必填字段不能为空")
        else:
            raise HTTPException(status_code=500, detail=f"创建支付申请失败: {error_msg}")

@router.get("", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = payment_list(db)
    res=[]
    for p in items:
        c = contract_get(db, p.contract_id)
        if not c:
            continue
        if u.role in ("ADMIN","AUDITOR","OWNER_CONTRACT","OWNER_FINANCE","OWNER_LEGAL","OWNER_LEADER","SUPERVISOR"):
            res.append(to_payment_out(p))
        elif u.role == "CONTRACTOR":
            if u.company is None or c.contractor_org == u.company:
                res.append(to_payment_out(p))
    return res

@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    return to_payment_out(p)

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
        # 不改变状态，保持在FINANCE_REVIEW，但标记为被拦截
        p.is_blocked = True
        over = round(p.amount - calc.max_apply, 2)
        msg = (f"申请金额超出可申请最大金额 {over} 元；"
               f"依据：批复概算={c.approved_budget}，完工比例={c.completion_ratio}，"
               f"可支付额度={calc.payable_limit}，已支付累计={c.paid_total}，"
               f"可申请最大金额={calc.max_apply}，申请金额={p.amount}")
        p.reject_reason = msg
        db.add(p); db.commit(); db.refresh(p)
        notify_create(db, "owner_contract", "超额支付预警单（demo）", f"{p.code}：{msg}")
        notify_create(db, p.created_by, "支付申请被拦截（超概算）", f"{p.code}：{msg}")
        audit_add(db, u.username, "BLOCK", "Payment", str(p.id), msg)
        return {"ok": False, "status": p.status, "is_blocked": True, "reason": msg}

    # 通过 -> 视为已支付
    p.status = "PAID"
    c.paid_total = round(c.paid_total + p.amount, 2)
    contract_update(db, c)
    db.add(p); db.commit(); db.refresh(p)

    notify_create(db, p.created_by, "支付已完成", f"{p.code} 已支付 {p.amount} 元")
    audit_add(db, u.username, "PAY", "Payment", str(p.id), f"paid {p.amount}")
    return {"ok": True, "status": p.status}

@router.post("/{payment_id}/review/finance/reject")
def finance_reject(payment_id: int, payload: PaymentReject, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("OWNER_FINANCE","ADMIN"))):
    p = payment_get(db, payment_id)
    if not p:
        raise HTTPException(404, "not found")
    p.status = "REJECTED"
    p.reject_reason = payload.reject_reason
    db.add(p); db.commit(); db.refresh(p)
    notify_create(db, p.created_by, "支付申请被驳回", f"{p.code} 已被驳回：{payload.reject_reason}")
    audit_add(db, u.username, "REJECT", "Payment", str(p.id), f"finance reject: {payload.reject_reason}")
    return {"ok": True, "status": p.status}
