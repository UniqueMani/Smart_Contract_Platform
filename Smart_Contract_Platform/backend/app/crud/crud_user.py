from sqlalchemy.orm import Session
from app.models.user import User

def user_get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def user_list(db: Session):
    return db.query(User).order_by(User.id.asc()).all()

def user_create(db: Session, username: str, hashed_password: str, role: str, company: str | None = None) -> User:
    u = User(username=username, hashed_password=hashed_password, role=role, company=company, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    return u
