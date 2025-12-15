from datetime import datetime
from pydantic import BaseModel

class NotificationOut(BaseModel):
    id: int
    title: str
    content: str
    is_read: bool
    created_at: datetime
