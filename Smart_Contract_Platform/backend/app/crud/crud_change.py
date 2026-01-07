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
    """获取当前用户待审核的变更申请任务
    
    只返回当前应该审批的任务，即：
    1. 该任务的状态是 PENDING
    2. 该任务之前的所有步骤都已经 APPROVED（或者该任务是第一步 step_order=1）
    """
    from app.models.change import ChangeRequest
    from sqlalchemy import and_, case
    
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
    
    # 获取所有匹配的任务
    all_tasks = query.order_by(ChangeApprovalTask.step_order.asc()).all()
    
    # 过滤：只返回当前应该审批的任务（前面的步骤都已通过）
    # 先收集所有相关变更申请的ID，批量查询所有任务
    change_ids = {task.change_id for task in all_tasks}
    change_tasks_map = {}  # change_id -> list of tasks (ordered by step_order)
    
    if change_ids:
        # 批量查询所有相关变更申请的任务
        all_change_tasks = db.query(ChangeApprovalTask).filter(
            ChangeApprovalTask.change_id.in_(change_ids)
        ).order_by(ChangeApprovalTask.change_id, ChangeApprovalTask.step_order).all()
        
        # 按变更申请ID分组
        for task in all_change_tasks:
            if task.change_id not in change_tasks_map:
                change_tasks_map[task.change_id] = []
            change_tasks_map[task.change_id].append(task)
    
    # 过滤：只返回当前应该审批的任务（前面的步骤都已通过）
    result = []
    for task in all_tasks:
        all_tasks_for_change = change_tasks_map.get(task.change_id, [])
        
        # 检查前面的步骤是否都已通过
        can_approve = True
        for t in all_tasks_for_change:
            if t.step_order < task.step_order:
                # 前面的步骤必须已通过
                if t.status != "APPROVED":
                    can_approve = False
                    break
        
        if can_approve:
            result.append(task)
    
    return result
