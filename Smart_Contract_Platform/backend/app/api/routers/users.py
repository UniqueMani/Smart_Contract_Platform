from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles, get_current_user, CurrentUser
from app.db.session import get_db
from app.crud.crud_user import user_list
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_roles("ADMIN"))):
    return [UserOut(username=u.username, role=u.role, company=u.company) for u in user_list(db)]

@router.get("/contractors", response_model=list[UserOut])
def list_contractors(db: Session = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    """获取所有承包方列表（用于合同创建时选择）"""
    all_users = user_list(db)
    contractors = [u for u in all_users if u.role == "CONTRACTOR" and u.company]
    # 去重，按公司名称返回
    companies = {}
    for contractor in contractors:
        if contractor.company and contractor.company not in companies:
            companies[contractor.company] = contractor.company
    return [UserOut(username="", role="CONTRACTOR", company=company) for company in sorted(companies.keys())]
