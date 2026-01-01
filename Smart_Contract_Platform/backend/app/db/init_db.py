from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base

from app.models import User, Contract
from app.core.security import get_password_hash
from app.services.rules import performance_bond

def create_all():
    # 删除所有表（用于开发环境，重新创建表结构）
    Base.metadata.drop_all(bind=engine)
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def seed(db: Session):
    # users
    def upsert_user(username: str, password: str, role: str, company: str | None = None, level: str | None = None):
        u = db.query(User).filter(User.username == username).first()
        if u:
            if level is not None:
                u.level = level
            return
        db.add(User(username=username, hashed_password=get_password_hash(password), role=role, company=company, level=level, is_active=True))

    upsert_user("owner_contract", "Owner123!", "OWNER_CONTRACT", company="发包方A")
    upsert_user("owner_finance", "Finance123!", "OWNER_FINANCE", company="发包方A")
    upsert_user("owner_legal", "Legal123!", "OWNER_LEGAL", company="发包方A")
    
    # 添加不同级别的领导用户
    upsert_user("owner_leader", "Leader123!", "OWNER_LEADER", company="发包方A", level="BUREAU_CHIEF")  # 局长
    upsert_user("owner_leader_section", "Section123!", "OWNER_LEADER", company="发包方A", level="SECTION_CHIEF")  # 科长
    upsert_user("owner_leader_director", "Director123!", "OWNER_LEADER", company="发包方A", level="DIRECTOR")  # 处长
    upsert_user("contractor", "Contractor123!", "CONTRACTOR", company="承包方B")
    upsert_user("supervisor", "Supervisor123!", "SUPERVISOR", company="监理单位C")
    upsert_user("auditor", "Auditor123!", "AUDITOR", company="审计机构D")
    upsert_user("admin", "Admin123!", "ADMIN", company=None)

    db.commit()

    # sample contract
    if not db.query(Contract).filter(Contract.contract_no == "HT-2025-001").first():
        tender = 10000000.0
        c = Contract(
            contract_no="HT-2025-001",
            contract_name="市政道路工程施工合同",
            project_name="市政道路工程一期",
            owner_org="发包方A",
            contractor_org="承包方B",
            tender_price=tender,
            contract_price=tender,
            performance_bond=performance_bond(tender),
            approved_budget=20000000.0,
            completion_ratio=0.40,
            paid_total=0.0,
            status="ACTIVE",
            created_by="owner_contract",
        )
        db.add(c); db.commit()

def main():
    create_all()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    print("✅ DB initialized: demo.db")

if __name__ == "__main__":
    main()
