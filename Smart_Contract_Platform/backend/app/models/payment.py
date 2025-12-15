from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # ZF-YYYY-XXX
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    amount: Mapped[float] = mapped_column(Float)
    purpose: Mapped[str] = mapped_column(String(300))
    progress_desc: Mapped[str] = mapped_column(String(500))
    period: Mapped[str] = mapped_column(String(32), default="")  # e.g., 2025-12

    status: Mapped[str] = mapped_column(String(32), default="DRAFT") # DRAFT/SUBMITTED/CONTRACT_REVIEW/FINANCE_REVIEW/BLOCKED/PAID/REJECTED
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="payments")
