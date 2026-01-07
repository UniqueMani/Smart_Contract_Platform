from datetime import datetime
from pydantic import BaseModel
from typing import Any


class StatCard(BaseModel):
    """统计卡片数据"""
    title: str
    value: str | int | float
    unit: str | None = None
    color: str | None = None  # 用于UI显示的颜色


class PendingItem(BaseModel):
    """待处理事项"""
    id: int
    title: str
    description: str | None = None
    link: str | None = None  # 跳转链接
    created_at: datetime | None = None


class RecentItem(BaseModel):
    """最近数据项"""
    id: int
    title: str
    description: str | None = None
    link: str | None = None
    created_at: datetime | None = None


class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    role: str
    stats: list[StatCard]  # 统计卡片列表
    pending_items: list[PendingItem]  # 待处理事项列表
    recent_items: list[RecentItem]  # 最近数据列表
    quick_actions: list[dict[str, Any]] | None = None  # 快捷操作

