from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.core.models import Base
from src.core.models.register import Register
from src.core.models.admin import Admin
from datetime import datetime

class Good(Base):
    __tablename__ = "good"
    GoodID: Mapped[int] = mapped_column(primary_key=True, index=True)
    TypeGood: Mapped[str] = mapped_column(String, index=True)
    NumberGood: Mapped[int] = mapped_column(Integer)
    GiventoWhome: Mapped[int] = mapped_column(ForeignKey("register.RegisterID"))
    GivenBy: Mapped[int] = mapped_column(ForeignKey("admin.AdminID"))
    CreatedDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships (optional, for ORM navigation)
    register: Mapped[Register] = relationship("Register")
    admin: Mapped[Admin] = relationship("Admin")
