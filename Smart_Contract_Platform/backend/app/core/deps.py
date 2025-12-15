from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.crud.crud_user import user_get_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class CurrentUser:
    def __init__(self, username: str, role: str, company: str | None):
        self.username = username
        self.role = role
        self.company = company

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        company: str | None = payload.get("company")
        if username is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = user_get_by_username(db, username)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return CurrentUser(username=user.username, role=user.role, company=user.company)

def require_roles(*roles: str):
    def _guard(u: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if u.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return u
    return _guard
