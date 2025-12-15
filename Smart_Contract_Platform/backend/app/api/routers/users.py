from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.crud.crud_user import user_list
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_roles("ADMIN"))):
    return [UserOut(username=u.username, role=u.role, company=u.company) for u in user_list(db)]
