from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class QuantityRecord(Base):
    __tablename__ = "quantity_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    period: Mapped[str] = mapped_column(String(32))  # e.g. 2025-12
    completion_ratio: Mapped[float] = mapped_column(Float)  # 0~1
    completion_description: Mapped[str] = mapped_column(String(2000))  # 完工情况描述（必填）
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # 签章相关字段
    sealed: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否已签章
    sealed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 签章人用户名
    sealed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 签章时间
    sealed_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 签章IP地址
