"""
AI审查相关的Schema定义
"""
from pydantic import BaseModel
from typing import List, Optional


class Issue(BaseModel):
    """问题项"""
    type: str  # 错误类型：风险/违规/不完善
    severity: str  # 严重程度：高/中/低
    location: str  # 位置描述（如"第3条"）
    description: str  # 问题描述
    suggestion: str  # 改进建议


class ReviewResult(BaseModel):
    """审查结果"""
    issues: List[Issue] = []  # 问题列表
    suggestions: List[str] = []  # 改进建议
    compliance_score: float = 0.0  # 合规性评分（0-100）
    reviewed_sections: List[str] = []  # 已审查的条款片段
    relevant_laws_count: int = 0  # 检索到的相关法律条款数量
    error: Optional[str] = None  # 错误信息（如果有）


class ReviewRequest(BaseModel):
    """审查请求（可选，支持自定义条款）"""
    clauses: Optional[str] = None  # 自定义条款内容，如果不提供则使用合同中的条款

