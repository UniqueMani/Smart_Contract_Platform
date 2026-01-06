from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import require_roles, get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.quantity import QuantityCreate, QuantityOut
from app.models.quantity import QuantityRecord
from app.crud.crud_quantity import quantity_create, quantity_list_for_contract
from app.crud.crud_contract import contract_get, contract_update
from app.crud.crud_audit import audit_add

router = APIRouter(prefix="/quantities", tags=["quantities"])

def to_quantity_out(q: QuantityRecord) -> QuantityOut:
    """将 SQLAlchemy 模型转换为 Pydantic 模型"""
    # 直接访问属性，避免 __dict__ 可能为空的问题
    return QuantityOut(
        id=q.id,
        contract_id=q.contract_id,
        period=q.period,
        completion_ratio=q.completion_ratio,
        note=q.note,
        created_by=q.created_by,
        created_at=q.created_at,
    )

@router.post("", response_model=QuantityOut)
def create_quantity(payload: QuantityCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("SUPERVISOR","ADMIN"))):
    # 验证必填字段
    if not payload.contract_id:
        raise HTTPException(status_code=400, detail="合同ID不能为空")
    if payload.completion_ratio is None or payload.completion_ratio < 0 or payload.completion_ratio > 1:
        raise HTTPException(status_code=400, detail="完工比例必须在0~1之间")
    if not payload.note or not payload.note.strip():
        raise HTTPException(status_code=400, detail="备注不能为空")
    
    c = contract_get(db, payload.contract_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"合同不存在 (ID: {payload.contract_id})")
    
    try:
        q = QuantityRecord(
            contract_id=payload.contract_id,
            period=payload.period or "",
            completion_ratio=payload.completion_ratio,
            note=payload.note,
            created_by=u.username,
            created_at=datetime.utcnow(),
        )
        q = quantity_create(db, q)
        # 同步到合同表（demo：用最新完工比例覆盖）
        c.completion_ratio = payload.completion_ratio
        contract_update(db, c)
        audit_add(db, u.username, "CREATE", "Quantity", str(q.id), f"set completion_ratio={payload.completion_ratio}")
        # 确保对象是最新的
        db.refresh(q)
        return to_quantity_out(q)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # 返回详细的错误信息
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg or "unique constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="该期次的完工比例已存在，请稍后重试")
        elif "FOREIGN KEY constraint failed" in error_msg or "foreign key constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="合同ID无效")
        elif "NOT NULL constraint failed" in error_msg or "not null constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="必填字段不能为空")
        else:
            raise HTTPException(status_code=500, detail=f"录入完工比例失败: {error_msg}")

@router.get("/contract/{contract_id}", response_model=list[QuantityOut])
def list_for_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = quantity_list_for_contract(db, contract_id)
    return [to_quantity_out(x) for x in items]
