from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_roles
from app.crud.crud_audit import audit_list
from app.schemas.audit import AuditOut

router = APIRouter(prefix="/audits", tags=["audits"])

@router.get("", response_model=list[AuditOut])
def list_audits(entity_type: str | None = None, entity_id: str | None = None, db: Session = Depends(get_db), _=Depends(require_roles("ADMIN","AUDITOR","OWNER_CONTRACT","OWNER_FINANCE","OWNER_LEGAL","OWNER_LEADER"))):
    items = audit_list(db, entity_type=entity_type, entity_id=entity_id)
    return [AuditOut(**x.__dict__) for x in items]
