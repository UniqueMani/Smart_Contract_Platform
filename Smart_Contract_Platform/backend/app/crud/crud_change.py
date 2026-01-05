from sqlalchemy.orm import Session
from app.models.change import ChangeRequest, ChangeApprovalTask

def change_create(db: Session, obj: ChangeRequest, commit: bool = True) -> ChangeRequest:
    db.add(obj)
    if commit:
        db.commit()
        db.refresh(obj)
    return obj

def change_get(db: Session, change_id: int) -> ChangeRequest | None:
    return db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()

def change_list(db: Session):
    return db.query(ChangeRequest).order_by(ChangeRequest.created_at.desc()).all()

def task_get(db: Session, task_id: int) -> ChangeApprovalTask | None:
    return db.query(ChangeApprovalTask).filter(ChangeApprovalTask.id == task_id).first()

def tasks_for_change(db: Session, change_id: int):
    return db.query(ChangeApprovalTask).filter(ChangeApprovalTask.change_id == change_id).order_by(ChangeApprovalTask.step_order.asc()).all()

def pending_tasks_for_user(db: Session, user_role: str, user_level: str | None):
    """获取当前用户待审核的变更申请任务"""
    from app.models.change import ChangeRequest
    # 查询状态为PENDING的任务，且角色匹配
    query = db.query(ChangeApprovalTask).join(ChangeRequest).filter(
        ChangeApprovalTask.status == "PENDING",
        ChangeApprovalTask.assignee_role == user_role,
        ChangeRequest.status == "APPROVING"
    )
    # 级别检查：
    # - 如果任务需要特定级别，用户必须有匹配的级别
    # - 如果任务不需要级别（required_level为None），任何该角色的用户都可以审核
    if user_level:
        # 用户有级别：可以审核需要该级别的任务，或不需要级别的任务
        query = query.filter(
            (ChangeApprovalTask.required_level == user_level) | 
            (ChangeApprovalTask.required_level.is_(None))
        )
    else:
        # 用户没有级别：只能审核不需要级别的任务（如OWNER_CONTRACT角色的任务）
        query = query.filter(ChangeApprovalTask.required_level.is_(None))
    
    return query.order_by(ChangeApprovalTask.step_order.asc()).all()
