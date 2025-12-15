from datetime import datetime
from app.models.change import ChangeApprovalTask

# 默认审批层级规则（可扩展为配置/规则引擎）
# 金额单位：万元
def steps_for_change_amount(amount_yuan: float) -> list[tuple[str, str]]:
    amt_wan = amount_yuan / 10000.0
    if amt_wan <= 5:
        return [("科员", "OWNER_CONTRACT"), ("科长", "OWNER_CONTRACT")]
    elif amt_wan <= 20:
        return [("科员", "OWNER_CONTRACT"), ("科长", "OWNER_CONTRACT"), ("处长", "OWNER_LEGAL")]
    elif amt_wan <= 100:
        return [("科员", "OWNER_CONTRACT"), ("科长", "OWNER_CONTRACT"), ("处长", "OWNER_LEGAL"), ("局长", "OWNER_LEADER")]
    else:
        return [("科员", "OWNER_CONTRACT"), ("科长", "OWNER_CONTRACT"), ("处长", "OWNER_LEGAL"), ("局长", "OWNER_LEADER"), ("特批", "OWNER_LEADER")]

def build_change_tasks(change_id: int, amount_yuan: float) -> list[ChangeApprovalTask]:
    steps = steps_for_change_amount(amount_yuan)
    tasks: list[ChangeApprovalTask] = []
    for idx, (name, role) in enumerate(steps, start=1):
        tasks.append(ChangeApprovalTask(change_id=change_id, step_order=idx, step_name=name, assignee_role=role))
    return tasks

def next_pending_task(tasks: list[ChangeApprovalTask]) -> ChangeApprovalTask | None:
    for t in sorted(tasks, key=lambda x: x.step_order):
        if t.status == "PENDING":
            return t
    return None

def is_all_approved(tasks: list[ChangeApprovalTask]) -> bool:
    return all(t.status == "APPROVED" for t in tasks)
