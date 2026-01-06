from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class QuantityRecord(Base):
    __tablename__ = "quantity_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    period: Mapped[str] = mapped_column(String(32))  # e.g. 2025-12
    completion_ratio: Mapped[float] = mapped_column(Float)  # 0~1
    note: Mapped[str] = mapped_column(String(500))  # 描述内容（必填）
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
