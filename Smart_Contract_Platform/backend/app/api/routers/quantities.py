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

@router.post("", response_model=QuantityOut)
def create_quantity(payload: QuantityCreate, db: Session = Depends(get_db), u: CurrentUser = Depends(require_roles("SUPERVISOR","ADMIN"))):
    c = contract_get(db, payload.contract_id)
    if not c:
        raise HTTPException(404, "contract not found")
    q = QuantityRecord(
        contract_id=payload.contract_id,
        period=payload.period,
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
    return QuantityOut(**q.__dict__)

@router.get("/contract/{contract_id}", response_model=list[QuantityOut])
def list_for_contract(contract_id: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = quantity_list_for_contract(db, contract_id)
    return [QuantityOut(**x.__dict__) for x in items]
