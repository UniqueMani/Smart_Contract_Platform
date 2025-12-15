from sqlalchemy.orm import Session
from app.models.quantity import QuantityRecord

def quantity_create(db: Session, obj: QuantityRecord) -> QuantityRecord:
    db.add(obj); db.commit(); db.refresh(obj); return obj

def quantity_list_for_contract(db: Session, contract_id: int):
    return db.query(QuantityRecord).filter(QuantityRecord.contract_id == contract_id).order_by(QuantityRecord.created_at.desc()).all()
