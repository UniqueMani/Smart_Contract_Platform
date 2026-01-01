from datetime import datetime
from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    contract_name: Mapped[str] = mapped_column(String(200))
    project_name: Mapped[str] = mapped_column(String(200))
    owner_org: Mapped[str] = mapped_column(String(200))
    contractor_org: Mapped[str] = mapped_column(String(200), index=True)

    tender_price: Mapped[float] = mapped_column(Float)   # 中标价
    contract_price: Mapped[float] = mapped_column(Float) # 合同价（强制=中标价）
    performance_bond: Mapped[float] = mapped_column(Float) # 履约保证金=中标价*10%

    approved_budget: Mapped[float] = mapped_column(Float)  # 批复概算
    completion_ratio: Mapped[float] = mapped_column(Float, default=0.0)  # 完工比例 0~1
    paid_total: Mapped[float] = mapped_column(Float, default=0.0)

    clauses: Mapped[str | None] = mapped_column(Text, nullable=True)  # 合同条款（支持后期智能审查）
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 合同开始日期
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 合同结束日期（用于审核超时检测和预警）

    status: Mapped[str] = mapped_column(String(32), default="DRAFT")  # DRAFT/APPROVING/ACTIVE/ARCHIVED

    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    changes = relationship("ChangeRequest", back_populates="contract", cascade="all, delete-orphan")
    payments = relationship("PaymentRequest", back_populates="contract", cascade="all, delete-orphan")
