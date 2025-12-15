from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app.crud.crud_user import user_get_by_username
from app.schemas.user import Token, UserOut
from app.core.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form: OAuth2PasswordRequestForm = Depends()):
    user = user_get_by_username(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(subject=user.username, role=user.role, company=user.company)
    return Token(access_token=token)

@router.get("/me", response_model=UserOut)
def me(u: CurrentUser = Depends(get_current_user)):
    return UserOut(username=u.username, role=u.role, company=u.company)
