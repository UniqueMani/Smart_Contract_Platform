from datetime import datetime
from app.models.change import ChangeApprovalTask

# 默认审批层级规则（可扩展为配置/规则引擎）
# 金额单位：万元
# 返回 (step_name, assignee_role, required_level)
def steps_for_change_amount(amount_yuan: float) -> list[tuple[str, str, str | None]]:
    # 如果金额为0，返回空列表（由时间审批规则处理，或合并逻辑处理）
    if amount_yuan == 0:
        return []
    amt_wan = amount_yuan / 10000.0
    if amt_wan <= 5:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF")
        ]
    elif amt_wan <= 20:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF"),
            ("处长", "OWNER_LEADER", "DIRECTOR")
        ]
    elif amt_wan <= 100:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF"),
            ("处长", "OWNER_LEADER", "DIRECTOR"),
            ("局长", "OWNER_LEADER", "BUREAU_CHIEF")
        ]
    else:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF"),
            ("处长", "OWNER_LEADER", "DIRECTOR"),
            ("局长", "OWNER_LEADER", "BUREAU_CHIEF"),
            ("特批", "OWNER_LEADER", "BUREAU_CHIEF")
        ]

def steps_for_schedule_days(days: int) -> list[tuple[str, str, str | None]]:
    """根据延长时间返回审批步骤"""
    if days <= 0:
        return []  # 无时间变更，返回空列表
    elif days <= 7:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF")
        ]
    elif days <= 30:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF"),
            ("处长", "OWNER_LEADER", "DIRECTOR")
        ]
    else:
        return [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF"),
            ("处长", "OWNER_LEADER", "DIRECTOR"),
            ("局长", "OWNER_LEADER", "BUREAU_CHIEF")
        ]

def merge_approval_steps(amount_steps: list, schedule_steps: list) -> list:
    """合并金额和时间审批步骤，取更严格的审批层级（步数更多的）"""
    # 如果只有金额变更，返回金额审批步骤
    if not schedule_steps:
        return amount_steps
    # 如果只有时间变更，返回时间审批步骤
    if not amount_steps:
        return schedule_steps
    
    # 两者都有变更，比较层级深度（步数），取更严格的
    amount_depth = len(amount_steps)
    schedule_depth = len(schedule_steps)
    
    if amount_depth >= schedule_depth:
        return amount_steps
    else:
        return schedule_steps

def build_change_tasks(change_id: int, amount_yuan: float, schedule_days: int = 0) -> list[ChangeApprovalTask]:
    """根据金额和延长时间构建审批任务"""
    amount_steps = steps_for_change_amount(amount_yuan)
    schedule_steps = steps_for_schedule_days(schedule_days)
    steps = merge_approval_steps(amount_steps, schedule_steps)
    
    # 如果合并后没有步骤（理论上不应该发生，因为至少金额或时间有变更），使用最低审批层级
    if not steps:
        steps = [
            ("合同管理员", "OWNER_CONTRACT", None),
            ("科长", "OWNER_LEADER", "SECTION_CHIEF")
        ]
    
    tasks: list[ChangeApprovalTask] = []
    for idx, (name, role, level) in enumerate(steps, start=1):
        tasks.append(ChangeApprovalTask(
            change_id=change_id,
            step_order=idx,
            step_name=name,
            assignee_role=role,
            required_level=level
        ))
    return tasks

def next_pending_task(tasks: list[ChangeApprovalTask]) -> ChangeApprovalTask | None:
    for t in sorted(tasks, key=lambda x: x.step_order):
        if t.status == "PENDING":
            return t
    return None

def is_all_approved(tasks: list[ChangeApprovalTask]) -> bool:
    return all(t.status == "APPROVED" for t in tasks)
