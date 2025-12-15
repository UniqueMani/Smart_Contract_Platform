from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.change import ChangeCreate, ChangeOut, ChangeTaskOut, TaskAction
from app.models.change import ChangeRequest
from app.crud.crud_change import change_create, change_get, change_list, task_get, tasks_for_change
from app.crud.crud_contract import contract_get, contract_update
from app.services.workflow import build_change_tasks, next_pending_task, is_all_approved
from app.crud.crud_notification import notify_create
from app.crud.crud_audit import audit_add

router = APIRouter(prefix="/changes", tags=["changes"])

def gen_code(prefix: str) -> str:
    yyyy = datetime.utcnow().strftime("%Y")
    rnd = random.randint(1, 999)
    return f"{prefix}-{yyyy}-{rnd:03d}"

@router.post("", response_model=ChangeOut)
def create_change(payload: ChangeCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("CONTRACTOR", "ADMIN"))):
    c = contract_get(db, payload.contract_id)
    if not c:
        raise HTTPException(404, "contract not found")
    if u.role == "CONTRACTOR" and u.company and c.contractor_org != u.company:
        raise HTTPException(403, "forbidden")
    ch = ChangeRequest(
        code=gen_code("BQ"),
        contract_id=payload.contract_id,
        amount=payload.amount,
        reason=payload.reason,
        scope_desc=payload.scope_desc,
        schedule_impact_days=payload.schedule_impact_days,
        status="SUBMITTED",
        created_by=u.username,
        created_at=datetime.utcnow(),
    )
    ch = change_create(db, ch)
    # build tasks
    tasks = build_change_tasks(ch.id, ch.amount)
    for t in tasks:
        db.add(t)
    ch.status = "APPROVING"
    db.commit(); db.refresh(ch)

    notify_create(db, to_username="owner_contract", title="新的变更申请待处理", content=f"{ch.code} 金额 {ch.amount} 元")
    audit_add(db, u.username, "CREATE", "Change", str(ch.id), f"submit change {ch.code}")
    return ChangeOut(**ch.__dict__)

@router.get("", response_model=list[ChangeOut])
def list_changes(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = change_list(db)
    res=[]
    for ch in items:
        c = contract_get(db, ch.contract_id)
        if not c:
            continue
        if u.role in ("ADMIN","AUDITOR","OWNER_CONTRACT","OWNER_FINANCE","OWNER_LEGAL","OWNER_LEADER","SUPERVISOR"):
            res.append(ChangeOut(**ch.__dict__))
        elif u.role == "CONTRACTOR":
            if u.company is None or c.contractor_org == u.company:
                res.append(ChangeOut(**ch.__dict__))
    return res

@router.get("/{change_id}", response_model=ChangeOut)
def get_change(change_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    ch = change_get(db, change_id)
    if not ch:
        raise HTTPException(404, "not found")
    return ChangeOut(**ch.__dict__)

@router.get("/{change_id}/tasks", response_model=list[ChangeTaskOut])
def get_tasks(change_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    ch = change_get(db, change_id)
    if not ch:
        raise HTTPException(404, "not found")
    tasks = tasks_for_change(db, change_id)
    return [ChangeTaskOut(**t.__dict__) for t in tasks]

@router.post("/tasks/{task_id}/approve")
def approve_task(task_id: int, payload: TaskAction, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    t = task_get(db, task_id)
    if not t:
        raise HTTPException(404, "task not found")
    if u.role not in ("ADMIN", t.assignee_role):
        raise HTTPException(403, "forbidden")
    if t.status != "PENDING":
        raise HTTPException(400, "task already handled")

    t.status="APPROVED"
    t.comment=payload.comment
    t.action_at=datetime.utcnow()
    db.add(t); db.commit(); db.refresh(t)

    ch = change_get(db, t.change_id)
    tasks = tasks_for_change(db, ch.id)
    if is_all_approved(tasks):
        ch.status="APPROVED"
        db.add(ch)
        # 变更通过后：触发支付额度重算（demo：不做复杂，只记录审计+通知）
        notify_create(db, "owner_finance", "变更审批通过", f"{ch.code} 已通过，建议检查支付额度重算")
        notify_create(db, ch.created_by, "变更审批通过", f"{ch.code} 已通过")
        audit_add(db, u.username, "APPROVE", "Change", str(ch.id), "all steps approved")
        db.commit()
    else:
        nxt = next_pending_task(tasks)
        if nxt:
            # 通知下一个角色（demo: 发固定账号名）
            role_to_user = {
                "OWNER_CONTRACT": "owner_contract",
                "OWNER_LEGAL": "owner_legal",
                "OWNER_LEADER": "owner_leader",
            }
            to_user = role_to_user.get(nxt.assignee_role, "owner_contract")
            notify_create(db, to_user, "变更审批待处理", f"{ch.code} 进入 {nxt.step_name} 节点")
            audit_add(db, u.username, "APPROVE", "ChangeTask", str(t.id), f"approve step {t.step_name}")
    return {"ok": True}

@router.post("/tasks/{task_id}/reject")
def reject_task(task_id: int, payload: TaskAction, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    t = task_get(db, task_id)
    if not t:
        raise HTTPException(404, "task not found")
    if u.role not in ("ADMIN", t.assignee_role):
        raise HTTPException(403, "forbidden")
    if t.status != "PENDING":
        raise HTTPException(400, "task already handled")

    t.status="REJECTED"
    t.comment=payload.comment
    t.action_at=datetime.utcnow()
    db.add(t)

    ch = change_get(db, t.change_id)
    ch.status="REJECTED"
    db.add(ch)

    notify_create(db, ch.created_by, "变更被驳回", f"{ch.code} 驳回原因：{payload.comment or '未填写'}")
    audit_add(db, u.username, "REJECT", "Change", str(ch.id), f"reject at {t.step_name}")
    db.commit()
    return {"ok": True}
