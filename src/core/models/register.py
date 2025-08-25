from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from src.core.models import sqlalchemy_model_to_pydantic
from src.core.models import Base
from pydantic import create_model
from src.core.models.admin import Admin

class Register(Base):
    __tablename__ = "register"
    RegisterID: Mapped[int] = mapped_column(primary_key=True, index=True)
    FirstName: Mapped[str] = mapped_column(nullable=False)
    LastName: Mapped[str] = mapped_column(nullable=False)
    Phone: Mapped[Optional[str]] = mapped_column()
    Email: Mapped[Optional[str]] = mapped_column()
    City: Mapped[Optional[str]] = mapped_column()
    Province: Mapped[Optional[str]] = mapped_column()
    Street: Mapped[Optional[str]] = mapped_column()
    NameFather: Mapped[Optional[str]] = mapped_column()
    NationalID: Mapped[Optional[str]] = mapped_column()
    CreatedBy: Mapped[Optional[int]] = mapped_column(ForeignKey("admin.AdminID"))
    MessageID: Mapped[Optional[int]] = mapped_column(ForeignKey("message.MessageID"))
    Age: Mapped[Optional[int]] = mapped_column()
    Region: Mapped[Optional[str]] = mapped_column()
    Gender: Mapped[Optional[str]] = mapped_column()
    HousebandFirstName: Mapped[Optional[str]] = mapped_column()
    HousbandLastName: Mapped[Optional[str]] = mapped_column()
    ReasonMissingHouseband: Mapped[Optional[str]] = mapped_column()
    UnderOrganizationName: Mapped[Optional[str]] = mapped_column()
    EducationLevel: Mapped[Optional[str]] = mapped_column()
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    IncomeForm: Mapped[Optional[str]] = mapped_column(Text)
    children_of_reg: Mapped[List["ChildrenOfRegistre"]] = relationship("ChildrenOfRegistre", back_populates="register")

class ChildrenOfRegistre(Base):
    __tablename__ = "children_of_registre"
    ChildrenOfRegistreID: Mapped[int] = mapped_column(primary_key=True, index=True)
    RegisterID: Mapped[int] = mapped_column(ForeignKey("register.RegisterID"))
    Age: Mapped[Optional[int]] = mapped_column()
    Gender: Mapped[Optional[str]] = mapped_column()
    NationalID: Mapped[Optional[str]] = mapped_column()
    FirstName: Mapped[Optional[str]] = mapped_column()
    LastName: Mapped[Optional[str]] = mapped_column()
    EducationLevel: Mapped[Optional[str]] = mapped_column()
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    register: Mapped[Register] = relationship("Register", back_populates="children_of_reg")

## create RegisterCreate pydantic model with sqlalchemy_model_to_pydantic
RegisterCreate = sqlalchemy_model_to_pydantic(Register, exclude=['RegisterID', 'CreatedDate', 'UpdatedDate'])
ChildrenOfRegistreCreate = sqlalchemy_model_to_pydantic(ChildrenOfRegistre, exclude=['ChildrenOfRegistreID', 'CreatedDate', 'UpdatedDate'])
## add ChildrenOfRegistreCreate to RegisterCreate as list
RegisterCreateWithChildren = create_model(
    "RegisterCreateWithChildren",
    __base__=RegisterCreate,
    children_of_registre=(Optional[list[ChildrenOfRegistreCreate]], None)
)