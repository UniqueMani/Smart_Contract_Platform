from sqlalchemy.orm import Session
from app.models.notification import Notification

def notify_create(db: Session, to_username: str, title: str, content: str) -> Notification:
    n = Notification(to_username=to_username, title=title, content=content, is_read=False)
    db.add(n); db.commit(); db.refresh(n); return n

def notify_list_for_user(db: Session, username: str):
    return db.query(Notification).filter(Notification.to_username == username).order_by(Notification.created_at.desc()).all()

def notify_get(db: Session, nid: int) -> Notification | None:
    return db.query(Notification).filter(Notification.id == nid).first()
