from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.dashboard import DashboardStats, StatCard, PendingItem, RecentItem
from app.models.contract import Contract
from app.models.change import ChangeRequest, ChangeApprovalTask
from app.models.payment import PaymentRequest
from app.models.audit import AuditLog
from app.models.quantity import QuantityRecord
from app.crud.crud_contract import contract_list
from app.crud.crud_change import change_list, pending_tasks_for_user
from app.crud.crud_payment import payment_list
from app.crud.crud_user import user_get_by_username
from app.crud.crud_audit import audit_list

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def can_view_contract(u: CurrentUser, c: Contract) -> bool:
    """判断用户是否可以查看合同"""
    if u.role in ("ADMIN", "AUDITOR", "OWNER_CONTRACT", "OWNER_STAFF", "OWNER_FINANCE", "OWNER_LEGAL", "OWNER_LEADER", "SUPERVISOR"):
        return True
    if u.role == "CONTRACTOR":
        return u.company is None or c.contractor_org == u.company
    return False


def can_view_change(u: CurrentUser, ch: ChangeRequest, contract: Contract) -> bool:
    """判断用户是否可以查看变更申请"""
    if u.role in ("ADMIN", "AUDITOR", "OWNER_CONTRACT", "OWNER_STAFF", "OWNER_FINANCE", "OWNER_LEGAL", "OWNER_LEADER", "SUPERVISOR"):
        return True
    if u.role == "CONTRACTOR":
        return u.company is None or contract.contractor_org == u.company
    return False


def can_view_payment(u: CurrentUser, p: PaymentRequest, contract: Contract) -> bool:
    """判断用户是否可以查看支付申请"""
    if u.role in ("ADMIN", "AUDITOR", "OWNER_CONTRACT", "OWNER_FINANCE", "OWNER_LEGAL", "OWNER_LEADER", "SUPERVISOR"):
        return True
    if u.role == "CONTRACTOR":
        return u.company is None or contract.contractor_org == u.company
    return False


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    """根据用户角色返回仪表盘统计数据"""
    
    stats = []
    pending_items = []
    recent_items = []
    quick_actions = []
    
    # 合同管理员仪表盘
    if u.role == "OWNER_CONTRACT":
        contracts = [c for c in contract_list(db) if c.created_by == u.username]
        draft_count = len([c for c in contracts if c.status == "DRAFT"])
        total_count = len(contracts)
        
        stats = [
            StatCard(title="草稿合同", value=draft_count, color="info"),
            StatCard(title="待提交合同", value=draft_count, color="warning"),
            StatCard(title="合同总数", value=total_count, color="primary"),
        ]
        
        # 待提交的合同
        pending_contracts = [c for c in contracts if c.status == "DRAFT"][:5]
        pending_items = [
            PendingItem(
                id=c.id,
                title=f"合同：{c.contract_name}",
                description=f"合同号：{c.contract_no}",
                link=f"/contracts/{c.id}",
                created_at=c.created_at
            )
            for c in pending_contracts
        ]
        
        # 最近创建的合同
        recent_contracts = sorted(contracts, key=lambda x: x.created_at, reverse=True)[:5]
        recent_items = [
            RecentItem(
                id=c.id,
                title=f"合同：{c.contract_name}",
                description=f"状态：{c.status}",
                link=f"/contracts/{c.id}",
                created_at=c.created_at
            )
            for c in recent_contracts
        ]
        
        quick_actions = [
            {"label": "新建合同", "link": "/contracts/new", "type": "primary"}
        ]
    
    # 法务仪表盘
    elif u.role == "OWNER_LEGAL":
        all_contracts = contract_list(db)
        pending_contracts = [c for c in all_contracts if c.status == "APPROVING"]
        pending_count = len(pending_contracts)
        
        # 统计已审核的合同（ACTIVE状态）
        reviewed_count = len([c for c in all_contracts if c.status == "ACTIVE"])
        
        stats = [
            StatCard(title="待审核合同", value=pending_count, color="warning"),
            StatCard(title="已审核合同", value=reviewed_count, color="success"),
        ]
        
        # 待审核合同列表
        pending_items = [
            PendingItem(
                id=c.id,
                title=f"合同：{c.contract_name}",
                description=f"合同号：{c.contract_no}，提交人：{c.created_by}",
                link=f"/contracts/{c.id}",
                created_at=c.created_at
            )
            for c in pending_contracts[:5]
        ]
        
        quick_actions = [
            {"label": "前往审核", "link": "/finance", "type": "primary"}
        ]
    
    # 财务仪表盘
    elif u.role == "OWNER_FINANCE":
        all_payments = payment_list(db)
        finance_review_payments = [p for p in all_payments if p.status == "FINANCE_REVIEW"]
        blocked_payments = [p for p in finance_review_payments if p.is_blocked]
        
        # 计算本月支付总额
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        month_payments = [p for p in all_payments if p.status == "PAID" and p.created_at >= month_start]
        month_total = sum(p.amount for p in month_payments)
        
        stats = [
            StatCard(title="待财务审核", value=len(finance_review_payments), color="warning"),
            StatCard(title="超额拦截", value=len(blocked_payments), color="danger"),
            StatCard(title="本月支付总额", value=f"{month_total:,.0f}", unit="元", color="success"),
        ]
        
        # 待审核支付申请
        pending_items = [
            PendingItem(
                id=p.id,
                title=f"支付申请：{p.code}",
                description=f"金额：{p.amount:,.0f} 元" + ("（已拦截）" if p.is_blocked else ""),
                link=f"/payments",
                created_at=p.created_at
            )
            for p in finance_review_payments[:5]
        ]
        
        quick_actions = [
            {"label": "前往财务审核", "link": "/finance", "type": "primary"}
        ]
    
    # 领导仪表盘（按级别）
    elif u.role == "OWNER_LEADER":
        user = user_get_by_username(db, u.username)
        if user:
            tasks = pending_tasks_for_user(db, u.role, user.level)
            pending_count = len(tasks)
            
            stats = [
                StatCard(title="待审批变更申请", value=pending_count, color="warning"),
            ]
            
            # 待审批变更申请列表
            pending_items = []
            for task in tasks[:5]:
                ch = db.query(ChangeRequest).filter(ChangeRequest.id == task.change_id).first()
                if ch:
                    level_name = {
                        "SECTION_CHIEF": "科长",
                        "DIRECTOR": "处长",
                        "BUREAU_CHIEF": "局长"
                    }.get(task.required_level or "", "无要求")
                    pending_items.append(
                        PendingItem(
                            id=ch.id,
                            title=f"变更申请：{ch.code}",
                            description=f"金额：{ch.amount:,.0f} 元，所需级别：{level_name}",
                            link=f"/changes",
                            created_at=ch.created_at
                        )
                    )
            
            quick_actions = [
                {"label": "前往审核", "link": "/finance", "type": "primary"}
            ]
    
    # 科员仪表盘
    elif u.role == "OWNER_STAFF":
        tasks = pending_tasks_for_user(db, u.role, None)
        pending_count = len(tasks)
        
        stats = [
            StatCard(title="待审批变更申请", value=pending_count, color="warning"),
        ]
        
        # 待审批变更申请列表
        pending_items = []
        for task in tasks[:5]:
            ch = db.query(ChangeRequest).filter(ChangeRequest.id == task.change_id).first()
            if ch:
                pending_items.append(
                    PendingItem(
                        id=ch.id,
                        title=f"变更申请：{ch.code}",
                        description=f"金额：{ch.amount:,.0f} 元",
                        link=f"/changes",
                        created_at=ch.created_at
                    )
                )
        
        quick_actions = [
            {"label": "前往审核", "link": "/finance", "type": "primary"}
        ]
    
    # 承包方仪表盘
    elif u.role == "CONTRACTOR":
        all_contracts = contract_list(db)
        my_contracts = [c for c in all_contracts if can_view_contract(u, c)]
        
        all_changes = change_list(db)
        my_changes = []
        for ch in all_changes:
            c = db.query(Contract).filter(Contract.id == ch.contract_id).first()
            if c and can_view_change(u, ch, c):
                my_changes.append(ch)
        
        all_payments = payment_list(db)
        my_payments = []
        for p in all_payments:
            c = db.query(Contract).filter(Contract.id == p.contract_id).first()
            if c and can_view_payment(u, p, c):
                my_payments.append(p)
        
        stats = [
            StatCard(title="我的合同", value=len(my_contracts), color="primary"),
            StatCard(title="我的变更申请", value=len(my_changes), color="info"),
            StatCard(title="我的支付申请", value=len(my_payments), color="success"),
        ]
        
        # 待处理的变更和支付申请
        pending_changes = [ch for ch in my_changes if ch.status in ("SUBMITTED", "APPROVING")][:3]
        pending_payments = [p for p in my_payments if p.status in ("FINANCE_REVIEW", "SUBMITTED")][:3]
        
        pending_items = []
        for ch in pending_changes:
            pending_items.append(
                PendingItem(
                    id=ch.id,
                    title=f"变更申请：{ch.code}",
                    description=f"状态：{ch.status}",
                    link=f"/changes",
                    created_at=ch.created_at
                )
            )
        for p in pending_payments:
            pending_items.append(
                PendingItem(
                    id=p.id,
                    title=f"支付申请：{p.code}",
                    description=f"状态：{p.status}",
                    link=f"/payments",
                    created_at=p.created_at
                )
            )
        
        quick_actions = [
            {"label": "提交变更申请", "link": "/changes", "type": "primary"},
            {"label": "提交支付申请", "link": "/payments", "type": "success"}
        ]
    
    # 监理仪表盘
    elif u.role == "SUPERVISOR":
        all_contracts = contract_list(db)
        active_contracts = [c for c in all_contracts if c.status == "ACTIVE"]
        
        # 统计需要录入完工比例的合同（ACTIVE状态且完工比例为0或很小）
        need_input = [c for c in active_contracts if c.completion_ratio < 0.01]
        
        # 统计已录入完工比例的合同
        contracts_with_quantity = []
        for c in active_contracts:
            quantities = db.query(QuantityRecord).filter(QuantityRecord.contract_id == c.id).all()
            if quantities:
                contracts_with_quantity.append(c)
        
        stats = [
            StatCard(title="需录入完工比例", value=len(need_input), color="warning"),
            StatCard(title="已录入完工比例", value=len(contracts_with_quantity), color="success"),
        ]
        
        # 需要录入完工比例的合同列表
        pending_items = [
            PendingItem(
                id=c.id,
                title=f"合同：{c.contract_name}",
                description=f"合同号：{c.contract_no}，当前完工比例：{c.completion_ratio:.0%}",
                link=f"/contracts/{c.id}",
                created_at=c.created_at
            )
            for c in need_input[:5]
        ]
        
        quick_actions = [
            {"label": "前往工程量页面", "link": "/quantity", "type": "primary"}
        ]
    
    # 审计仪表盘
    elif u.role == "AUDITOR":
        all_audits = audit_list(db)
        total_count = len(all_audits)
        
        # 今日操作数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_audits = [a for a in all_audits if a.created_at >= today_start]
        today_count = len(today_audits)
        
        stats = [
            StatCard(title="审计日志总数", value=total_count, color="primary"),
            StatCard(title="今日操作数", value=today_count, color="info"),
        ]
        
        # 最近审计日志
        recent_items = [
            RecentItem(
                id=a.id,
                title=f"{a.action} - {a.entity_type}",
                description=f"操作人：{a.actor}，详情：{a.detail[:50]}",
                link=f"/audits",
                created_at=a.created_at
            )
            for a in all_audits[:5]
        ]
        
        quick_actions = [
            {"label": "查看审计日志", "link": "/audits", "type": "primary"}
        ]
    
    # 管理员仪表盘
    elif u.role == "ADMIN":
        all_contracts = contract_list(db)
        all_changes = change_list(db)
        all_payments = payment_list(db)
        all_audits = audit_list(db)
        
        # 合同统计
        draft_contracts = [c for c in all_contracts if c.status == "DRAFT"]
        approving_contracts = [c for c in all_contracts if c.status == "APPROVING"]
        active_contracts = [c for c in all_contracts if c.status == "ACTIVE"]
        archived_contracts = [c for c in all_contracts if c.status == "ARCHIVED"]
        
        # 变更统计
        approving_changes = [ch for ch in all_changes if ch.status == "APPROVING"]
        approved_changes = [ch for ch in all_changes if ch.status == "APPROVED"]
        rejected_changes = [ch for ch in all_changes if ch.status == "REJECTED"]
        
        # 支付统计
        finance_review_payments = [p for p in all_payments if p.status == "FINANCE_REVIEW"]
        paid_payments = [p for p in all_payments if p.status == "PAID"]
        blocked_payments = [p for p in finance_review_payments if p.is_blocked]
        total_paid = sum(p.amount for p in paid_payments)
        
        # 审计日志统计
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_audits = [a for a in all_audits if a.created_at >= today_start]
        
        stats = [
            StatCard(title="合同总数", value=len(all_contracts), color="primary"),
            StatCard(title="草稿合同", value=len(draft_contracts), color="info"),
            StatCard(title="待审核合同", value=len(approving_contracts), color="warning"),
            StatCard(title="生效合同", value=len(active_contracts), color="success"),
            StatCard(title="变更总数", value=len(all_changes), color="info"),
            StatCard(title="待审批变更", value=len(approving_changes), color="warning"),
            StatCard(title="已审批变更", value=len(approved_changes), color="success"),
            StatCard(title="支付总数", value=len(all_payments), color="primary"),
            StatCard(title="待财务审核", value=len(finance_review_payments), color="warning"),
            StatCard(title="超额拦截", value=len(blocked_payments), color="danger"),
            StatCard(title="累计支付", value=f"{total_paid:,.0f}", unit="元", color="success"),
            StatCard(title="审计日志总数", value=len(all_audits), color="info"),
            StatCard(title="今日操作数", value=len(today_audits), color="info"),
        ]
        
        # 待处理事项
        pending_items = []
        for c in approving_contracts[:3]:
            pending_items.append(
                PendingItem(
                    id=c.id,
                    title=f"待审核合同：{c.contract_name}",
                    description=f"合同号：{c.contract_no}，提交人：{c.created_by}",
                    link=f"/contracts/{c.id}",
                    created_at=c.created_at
                )
            )
        for ch in approving_changes[:3]:
            pending_items.append(
                PendingItem(
                    id=ch.id,
                    title=f"待审批变更：{ch.code}",
                    description=f"金额：{ch.amount:,.0f} 元，状态：{ch.status}",
                    link=f"/changes",
                    created_at=ch.created_at
                )
            )
        for p in finance_review_payments[:3]:
            blocked_text = "（已拦截）" if p.is_blocked else ""
            pending_items.append(
                PendingItem(
                    id=p.id,
                    title=f"待财务审核：{p.code}{blocked_text}",
                    description=f"金额：{p.amount:,.0f} 元，申请人：{p.created_by}",
                    link=f"/payments",
                    created_at=p.created_at
                )
            )
        
        # 最近数据
        recent_items = []
        # 最近创建的合同
        recent_contracts = sorted(all_contracts, key=lambda x: x.created_at, reverse=True)[:3]
        for c in recent_contracts:
            recent_items.append(
                RecentItem(
                    id=c.id,
                    title=f"合同：{c.contract_name}",
                    description=f"合同号：{c.contract_no}，状态：{c.status}",
                    link=f"/contracts/{c.id}",
                    created_at=c.created_at
                )
            )
        # 最近的审计日志
        recent_audits = sorted(all_audits, key=lambda x: x.created_at, reverse=True)[:3]
        for a in recent_audits:
            recent_items.append(
                RecentItem(
                    id=a.id,
                    title=f"{a.action} - {a.entity_type}",
                    description=f"操作人：{a.actor}，详情：{a.detail[:50]}",
                    link=f"/audits",
                    created_at=a.created_at
                )
            )
        
        quick_actions = [
            {"label": "合同管理", "link": "/contracts", "type": "primary"},
            {"label": "变更管理", "link": "/changes", "type": "info"},
            {"label": "支付管理", "link": "/payments", "type": "success"},
            {"label": "审核页面", "link": "/finance", "type": "warning"},
            {"label": "审计日志", "link": "/audits", "type": "info"},
        ]
    
    # 默认仪表盘（其他角色）
    else:
        stats = [
            StatCard(title="欢迎", value="使用系统", color="primary"),
        ]
    
    return DashboardStats(
        role=u.role,
        stats=stats,
        pending_items=pending_items,
        recent_items=recent_items,
        quick_actions=quick_actions
    )

