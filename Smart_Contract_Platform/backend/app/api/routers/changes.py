from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.change import ChangeCreate, ChangeOut, ChangeTaskOut, TaskAction, ChangeWithTaskOut
from app.models.change import ChangeRequest
from app.crud.crud_change import change_create, change_get, change_list, task_get, tasks_for_change, pending_tasks_for_user
from app.crud.crud_contract import contract_get, contract_update
from app.crud.crud_user import user_get_by_username
from app.services.workflow import build_change_tasks, next_pending_task, is_all_approved
from app.crud.crud_notification import notify_create
from app.crud.crud_audit import audit_add

router = APIRouter(prefix="/changes", tags=["changes"])

def gen_code(prefix: str, db: Session) -> str:
    """生成唯一的变更单号，如果重复则重试"""
    yyyy = datetime.utcnow().strftime("%Y")
    max_attempts = 10
    for _ in range(max_attempts):
        rnd = random.randint(1, 999)
        code = f"{prefix}-{yyyy}-{rnd:03d}"
        # 检查是否已存在
        existing = db.query(ChangeRequest).filter(ChangeRequest.code == code).first()
        if not existing:
            return code
    # 如果10次都重复（极不可能），使用时间戳
    import time
    return f"{prefix}-{yyyy}-{int(time.time()) % 10000:04d}"

@router.post("", response_model=ChangeOut)
def create_change(payload: ChangeCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("CONTRACTOR", "ADMIN"))):
    # 验证必填字段
    if not payload.contract_id:
        raise HTTPException(400, "合同ID不能为空")
    if payload.amount is None or payload.amount < 0:
        raise HTTPException(400, "变更金额不能为负数")
    # 允许金额为0（可以只变更时间），但需要至少金额或时间有变更
    if payload.amount == 0 and (not payload.schedule_impact_days or payload.schedule_impact_days == 0):
        raise HTTPException(400, "变更金额和时间不能同时为0，至少需要变更其中一项")
    if not payload.reason or not payload.reason.strip():
        raise HTTPException(400, "变更原因不能为空")
    if not payload.scope_desc or not payload.scope_desc.strip():
        raise HTTPException(400, "范围描述不能为空")
    
    c = contract_get(db, payload.contract_id)
    if not c:
        raise HTTPException(404, f"合同不存在 (ID: {payload.contract_id})")
    if u.role == "CONTRACTOR" and u.company and c.contractor_org != u.company:
        raise HTTPException(403, "无权操作此合同的变更申请")
    try:
        ch = ChangeRequest(
            code=gen_code("BQ", db),
            contract_id=payload.contract_id,
            amount=payload.amount,
            reason=payload.reason,
            scope_desc=payload.scope_desc,
            schedule_impact_days=payload.schedule_impact_days or 0,
            status="SUBMITTED",
            created_by=u.username,
            created_at=datetime.utcnow(),
        )
        ch = change_create(db, ch, commit=False)
        # flush 以获取 id，但不提交事务
        db.flush()
        # build tasks - 现在 ch.id 已经有值了
        # 传入金额和延长时间，系统会自动合并审批层级，取更严格的
        tasks = build_change_tasks(ch.id, ch.amount, ch.schedule_impact_days)
        for t in tasks:
            db.add(t)
        # 如果创建了审批任务，说明已进入审批流程，状态改为 APPROVING
        # 如果没有审批任务（理论上不应该发生），保持 SUBMITTED 状态
        if tasks:
            ch.status = "APPROVING"
        # 通知合同管理员（审批流程第一步）
        if ch.amount > 0:
            notify_content = f"{ch.code} 金额 {ch.amount} 元"
        else:
            notify_content = f"{ch.code} 时间变更 {ch.schedule_impact_days} 天"
        if ch.amount > 0 and ch.schedule_impact_days > 0:
            notify_content = f"{ch.code} 金额 {ch.amount} 元，时间变更 {ch.schedule_impact_days} 天"
        notify_create(db, to_username="owner_contract", title="新的变更申请待处理", content=f"{notify_content}，请进行合同管理员审核", commit=False)
        audit_add(db, u.username, "CREATE", "Change", str(ch.id), f"submit change {ch.code}", commit=False)
        db.commit()
        db.refresh(ch)
        # 修复：直接访问属性而不是使用 __dict__
        return ChangeOut(
            id=ch.id,
            code=ch.code,
            contract_id=ch.contract_id,
            amount=ch.amount,
            reason=ch.reason,
            scope_desc=ch.scope_desc,
            schedule_impact_days=ch.schedule_impact_days,
            status=ch.status,
            created_by=ch.created_by,
            created_at=ch.created_at,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # 返回详细的错误信息
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg:
            raise HTTPException(400, "变更单号已存在，请稍后重试")
        elif "FOREIGN KEY constraint failed" in error_msg:
            raise HTTPException(400, "合同ID无效")
        else:
            raise HTTPException(500, f"创建变更申请失败: {error_msg}")

@router.get("", response_model=list[ChangeOut])
def list_changes(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = change_list(db)
    res=[]
    for ch in items:
        c = contract_get(db, ch.contract_id)
        if not c:
            continue
        # 修复：直接访问属性而不是使用 __dict__
        change_out = ChangeOut(
            id=ch.id,
            code=ch.code,
            contract_id=ch.contract_id,
            amount=ch.amount,
            reason=ch.reason,
            scope_desc=ch.scope_desc,
            schedule_impact_days=ch.schedule_impact_days,
            status=ch.status,
            created_by=ch.created_by,
            created_at=ch.created_at,
        )
        if u.role in ("ADMIN","AUDITOR","OWNER_CONTRACT","OWNER_FINANCE","OWNER_LEGAL","OWNER_LEADER","SUPERVISOR"):
            res.append(change_out)
        elif u.role == "CONTRACTOR":
            if u.company is None or c.contractor_org == u.company:
                res.append(change_out)
    return res

@router.get("/{change_id}", response_model=ChangeOut)
def get_change(change_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    ch = change_get(db, change_id)
    if not ch:
        raise HTTPException(404, "not found")
    # 修复：直接访问属性而不是使用 __dict__
    return ChangeOut(
        id=ch.id,
        code=ch.code,
        contract_id=ch.contract_id,
        amount=ch.amount,
        reason=ch.reason,
        scope_desc=ch.scope_desc,
        schedule_impact_days=ch.schedule_impact_days,
        status=ch.status,
        created_by=ch.created_by,
        created_at=ch.created_at,
    )

@router.get("/{change_id}/tasks", response_model=list[ChangeTaskOut])
def get_tasks(change_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    ch = change_get(db, change_id)
    if not ch:
        raise HTTPException(404, "not found")
    tasks = tasks_for_change(db, change_id)
    # 修复：直接访问属性而不是使用 __dict__
    return [
        ChangeTaskOut(
            id=t.id,
            change_id=t.change_id,
            step_order=t.step_order,
            step_name=t.step_name,
            assignee_role=t.assignee_role,
            required_level=t.required_level,
            status=t.status,
            comment=t.comment,
            action_at=t.action_at,
        )
        for t in tasks
    ]

@router.get("/pending/my", response_model=list[ChangeWithTaskOut])
def get_my_pending_changes(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    """获取当前用户待审核的变更申请"""
    user = user_get_by_username(db, u.username)
    if not user:
        raise HTTPException(404, "user not found")
    
    tasks = pending_tasks_for_user(db, u.role, user.level)
    result = []
    for task in tasks:
        ch = change_get(db, task.change_id)
        if ch:
            # 修复：直接访问属性而不是使用 __dict__
            result.append(ChangeWithTaskOut(
                change=ChangeOut(
                    id=ch.id,
                    code=ch.code,
                    contract_id=ch.contract_id,
                    amount=ch.amount,
                    reason=ch.reason,
                    scope_desc=ch.scope_desc,
                    schedule_impact_days=ch.schedule_impact_days,
                    status=ch.status,
                    created_by=ch.created_by,
                    created_at=ch.created_at,
                ),
                task=ChangeTaskOut(
                    id=task.id,
                    change_id=task.change_id,
                    step_order=task.step_order,
                    step_name=task.step_name,
                    assignee_role=task.assignee_role,
                    required_level=task.required_level,
                    status=task.status,
                    comment=task.comment,
                    action_at=task.action_at,
                )
            ))
    return result

@router.post("/tasks/{task_id}/approve")
def approve_task(task_id: int, payload: TaskAction, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    t = task_get(db, task_id)
    if not t:
        raise HTTPException(404, "task not found")
    
    # 权限检查：管理员或角色匹配
    if u.role != "ADMIN" and u.role != t.assignee_role:
        raise HTTPException(403, "forbidden")
    
    # 级别检查：如果任务需要特定级别，检查用户级别
    if t.required_level is not None and u.role != "ADMIN":
        user = user_get_by_username(db, u.username)
        if not user or user.level != t.required_level:
            raise HTTPException(403, f"需要级别 {t.required_level}，当前用户级别不匹配")
    
    if t.status != "PENDING":
        raise HTTPException(400, "task already handled")

    try:
        t.status="APPROVED"
        t.comment=payload.comment
        t.action_at=datetime.utcnow()
        db.add(t)

        ch = change_get(db, t.change_id)
        tasks = tasks_for_change(db, ch.id)
        if is_all_approved(tasks):
            ch.status="APPROVED"
            db.add(ch)
            # 变更通过后：更新合同信息
            c = contract_get(db, ch.contract_id)
            if c:
                update_messages = []
                # 更新合同价（如果有金额变更）
                if ch.amount > 0:
                    old_contract_price = c.contract_price
                    c.contract_price = round(c.contract_price + ch.amount, 2)
                    update_messages.append(f"合同价从 {old_contract_price} 调整为 {c.contract_price}（变更金额：{ch.amount}）")
                
                # 更新合同结束日期（如果有时间变更）
                if ch.schedule_impact_days > 0 and c.end_date:
                    from datetime import timedelta
                    old_end_date = c.end_date
                    c.end_date = c.end_date + timedelta(days=ch.schedule_impact_days)
                    update_messages.append(f"合同结束日期从 {old_end_date.strftime('%Y-%m-%d')} 延长至 {c.end_date.strftime('%Y-%m-%d')}（延长 {ch.schedule_impact_days} 天）")
                elif ch.schedule_impact_days > 0 and not c.end_date:
                    # 如果合同没有结束日期，但需要延长，可以设置一个默认日期
                    from datetime import timedelta
                    if c.start_date:
                        c.end_date = c.start_date + timedelta(days=ch.schedule_impact_days)
                        update_messages.append(f"合同结束日期设置为 {c.end_date.strftime('%Y-%m-%d')}（延长 {ch.schedule_impact_days} 天）")
                
                if update_messages:
                    contract_update(db, c, commit=False)
                    audit_msg = f"变更审批通过，{'；'.join(update_messages)}"
                    audit_add(db, u.username, "UPDATE", "Contract", str(c.id), audit_msg, commit=False)
                
                # 生成通知内容
                notify_details = []
                if ch.amount > 0:
                    notify_details.append("合同价已更新")
                if ch.schedule_impact_days > 0:
                    notify_details.append("合同结束日期已更新")
                notify_detail_text = "，".join(notify_details) if notify_details else "变更已生效"
                
                # 变更审批通过后：通知财务（需要重算支付额度）和申请创建人（承包方）
                # 不通知合同管理员，因为合同管理员主要负责合同创建和变更申请的第一步审批
                notify_create(db, "owner_finance", "变更审批通过", f"{ch.code} 已通过，{notify_detail_text}，建议检查支付额度重算", commit=False)
                notify_create(db, ch.created_by, "变更审批通过", f"{ch.code} 已通过，{notify_detail_text}", commit=False)
            audit_add(db, u.username, "APPROVE", "Change", str(ch.id), "all steps approved", commit=False)
        else:
            nxt = next_pending_task(tasks)
            if nxt:
                # 根据角色和级别查找对应的用户
                if nxt.assignee_role == "OWNER_LEADER" and nxt.required_level:
                    # 对于领导角色，需要根据级别查找对应的用户
                    from app.models.user import User
                    target_user = db.query(User).filter(
                        User.role == "OWNER_LEADER",
                        User.level == nxt.required_level
                    ).first()
                    if target_user:
                        to_user = target_user.username
                    else:
                        # 如果找不到对应级别的用户，使用默认映射
                        level_to_user = {
                            "SECTION_CHIEF": "owner_leader_section",
                            "DIRECTOR": "owner_leader_director",
                            "BUREAU_CHIEF": "owner_leader",
                        }
                        to_user = level_to_user.get(nxt.required_level, "owner_leader")
                else:
                    # 对于其他角色，使用固定账号名
                    role_to_user = {
                        "OWNER_CONTRACT": "owner_contract",
                        "OWNER_LEGAL": "owner_legal",
                        "OWNER_LEADER": "owner_leader",
                    }
                    to_user = role_to_user.get(nxt.assignee_role, "owner_contract")
                notify_create(db, to_user, "变更审批待处理", f"{ch.code} 进入 {nxt.step_name} 节点", commit=False)
                audit_add(db, u.username, "APPROVE", "ChangeTask", str(t.id), f"approve step {t.step_name}", commit=False)
        db.commit()
        db.refresh(t)
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise

@router.post("/tasks/{task_id}/reject")
def reject_task(task_id: int, payload: TaskAction, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    t = task_get(db, task_id)
    if not t:
        raise HTTPException(404, "task not found")
    
    # 权限检查：管理员或角色匹配
    if u.role != "ADMIN" and u.role != t.assignee_role:
        raise HTTPException(403, "forbidden")
    
    # 级别检查：如果任务需要特定级别，检查用户级别
    if t.required_level is not None and u.role != "ADMIN":
        user = user_get_by_username(db, u.username)
        if not user or user.level != t.required_level:
            raise HTTPException(403, f"需要级别 {t.required_level}，当前用户级别不匹配")
    
    if t.status != "PENDING":
        raise HTTPException(400, "task already handled")

    try:
        t.status="REJECTED"
        t.comment=payload.comment
        t.action_at=datetime.utcnow()
        db.add(t)

        ch = change_get(db, t.change_id)
        ch.status="REJECTED"
        db.add(ch)

        notify_create(db, ch.created_by, "变更被驳回", f"{ch.code} 驳回原因：{payload.comment or '未填写'}", commit=False)
        audit_add(db, u.username, "REJECT", "Change", str(ch.id), f"reject at {t.step_name}", commit=False)
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise
