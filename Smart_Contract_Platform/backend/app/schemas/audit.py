from datetime import datetime
from pydantic import BaseModel

class AuditOut(BaseModel):
    id: int
    actor: str
    action: str
    entity_type: str
    entity_id: str
    detail: str
    created_at: datetime
