from sqlalchemy.orm import Session
from app.models.change import ChangeRequest, ChangeApprovalTask

def change_create(db: Session, obj: ChangeRequest) -> ChangeRequest:
    db.add(obj); db.commit(); db.refresh(obj); return obj

def change_get(db: Session, change_id: int) -> ChangeRequest | None:
    return db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()

def change_list(db: Session):
    return db.query(ChangeRequest).order_by(ChangeRequest.created_at.desc()).all()

def task_get(db: Session, task_id: int) -> ChangeApprovalTask | None:
    return db.query(ChangeApprovalTask).filter(ChangeApprovalTask.id == task_id).first()

def tasks_for_change(db: Session, change_id: int):
    return db.query(ChangeApprovalTask).filter(ChangeApprovalTask.change_id == change_id).order_by(ChangeApprovalTask.step_order.asc()).all()
