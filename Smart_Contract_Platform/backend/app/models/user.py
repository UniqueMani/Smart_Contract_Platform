from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(64), index=True)
    company: Mapped[str | None] = mapped_column(String(128), nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True)  # 级别：SECTION_CHIEF(科长), DIRECTOR(处长), BUREAU_CHIEF(局长)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
