from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # BQ-YYYY-XXX
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    amount: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String(500))
    scope_desc: Mapped[str] = mapped_column(String(500))
    schedule_impact_days: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(32), default="DRAFT")  # DRAFT/SUBMITTED/APPROVING/APPROVED/REJECTED
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="changes")
    tasks = relationship("ChangeApprovalTask", back_populates="change", cascade="all, delete-orphan")

class ChangeApprovalTask(Base):
    __tablename__ = "change_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    change_id: Mapped[int] = mapped_column(ForeignKey("change_requests.id"))
    step_order: Mapped[int] = mapped_column(Integer)
    step_name: Mapped[str] = mapped_column(String(64))  # 科员/科长/处长/局长/特批
    assignee_role: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="PENDING") # PENDING/APPROVED/REJECTED/SKIPPED
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    action_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    change = relationship("ChangeRequest", back_populates="tasks")
