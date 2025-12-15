from sqlalchemy.orm import Session
from app.models.contract import Contract

def contract_create(db: Session, obj: Contract) -> Contract:
    db.add(obj); db.commit(); db.refresh(obj); return obj

def contract_get(db: Session, contract_id: int) -> Contract | None:
    return db.query(Contract).filter(Contract.id == contract_id).first()

def contract_get_by_no(db: Session, contract_no: str) -> Contract | None:
    return db.query(Contract).filter(Contract.contract_no == contract_no).first()

def contract_list(db: Session):
    return db.query(Contract).order_by(Contract.created_at.desc()).all()

def contract_update(db: Session, c: Contract) -> Contract:
    db.add(c); db.commit(); db.refresh(c); return c
