from sqlalchemy.orm import Session
from app.models.contract import Contract

def contract_create(db: Session, obj: Contract, commit: bool = True) -> Contract:
    db.add(obj)
    if commit:
        db.commit()
        db.refresh(obj)
    return obj

def contract_get(db: Session, contract_id: int) -> Contract | None:
    return db.query(Contract).filter(Contract.id == contract_id).first()

def contract_get_by_no(db: Session, contract_no: str) -> Contract | None:
    return db.query(Contract).filter(Contract.contract_no == contract_no).first()

def contract_list(db: Session, search: str | None = None, contract_no: str | None = None, contract_name: str | None = None):
    query = db.query(Contract)
    if search:
        # 单个搜索参数：同时搜索合同名称或合同号（OR 关系）
        query = query.filter(
            (Contract.contract_name.contains(search)) | (Contract.contract_no.contains(search))
        )
    else:
        # 独立参数：向后兼容（AND 关系）
        if contract_no:
            query = query.filter(Contract.contract_no.contains(contract_no))
        if contract_name:
            query = query.filter(Contract.contract_name.contains(contract_name))
    return query.order_by(Contract.created_at.desc()).all()

def contract_update(db: Session, c: Contract, commit: bool = True) -> Contract:
    db.add(c)
    if commit:
        db.commit()
        db.refresh(c)
    return c
