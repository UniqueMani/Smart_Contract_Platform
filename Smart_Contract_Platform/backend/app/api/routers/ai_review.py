"""
AI合同审查API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles, CurrentUser
from app.db.session import get_db
from app.schemas.ai_review import ReviewResult, ReviewRequest
from app.crud.crud_contract import contract_get
from app.services.ai_review import get_ai_review_service
from app.crud.crud_audit import audit_add

router = APIRouter(prefix="/contracts", tags=["ai-review"])


@router.post("/{contract_id}/ai-review", response_model=ReviewResult)
def review_contract(
    contract_id: int,
    payload: ReviewRequest | None = None,
    db: Session = Depends(get_db),
    u: CurrentUser = Depends(require_roles("OWNER_CONTRACT", "OWNER_LEGAL", "ADMIN"))
):
    """
    AI审查合同条款
    
    如果payload.clauses不为空，则审查自定义条款；否则审查合同中的条款
    """
    # 获取合同信息
    contract = contract_get(db, contract_id)
    if not contract:
        raise HTTPException(404, "合同不存在")
    
    # 确定要审查的条款内容
    clauses_to_review = payload.clauses if payload and payload.clauses else contract.clauses
    
    if not clauses_to_review or not clauses_to_review.strip():
        raise HTTPException(400, "合同条款为空，无法进行审查")
    
    try:
        # 获取AI审查服务
        ai_service = get_ai_review_service()
        
        # 执行审查
        result = ai_service.review_contract(clauses_to_review)
        
        # 记录审计日志
        try:
            audit_add(
                db,
                u.username,
                "AI_REVIEW",
                "Contract",
                str(contract_id),
                f"AI审查合同条款，合规性评分: {result.get('compliance_score', 0.0)}",
                commit=True
            )
        except Exception:
            # 审计日志记录失败不影响审查结果返回
            pass
        
        return ReviewResult(**result)
    except Exception as e:
        raise HTTPException(500, f"AI审查失败: {str(e)}")

