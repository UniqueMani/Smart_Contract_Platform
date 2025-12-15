from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.crud.crud_notification import notify_list_for_user, notify_get
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=list[NotificationOut])
def list_my(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    items = notify_list_for_user(db, u.username)
    return [NotificationOut(id=n.id, title=n.title, content=n.content, is_read=n.is_read, created_at=n.created_at) for n in items]

@router.post("/{nid}/read")
def mark_read(nid: int, db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    n = notify_get(db, nid)
    if not n or n.to_username != u.username:
        raise HTTPException(404, "not found")
    n.is_read = True
    db.add(n); db.commit()
    return {"ok": True}
