from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def audit_add(db: Session, actor: str, action: str, entity_type: str, entity_id: str, detail: str):
    db.add(AuditLog(actor=actor, action=action, entity_type=entity_type, entity_id=str(entity_id), detail=detail))
    db.commit()

def audit_list(db: Session, entity_type: str | None = None, entity_id: str | None = None):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        q = q.filter(AuditLog.entity_id == str(entity_id))
    return q.order_by(AuditLog.created_at.desc()).all()
