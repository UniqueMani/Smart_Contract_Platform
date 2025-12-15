from sqlalchemy.orm import Session
from app.models.payment import PaymentRequest

def payment_create(db: Session, obj: PaymentRequest) -> PaymentRequest:
    db.add(obj); db.commit(); db.refresh(obj); return obj

def payment_get(db: Session, payment_id: int) -> PaymentRequest | None:
    return db.query(PaymentRequest).filter(PaymentRequest.id == payment_id).first()

def payment_list(db: Session):
    return db.query(PaymentRequest).order_by(PaymentRequest.created_at.desc()).all()
