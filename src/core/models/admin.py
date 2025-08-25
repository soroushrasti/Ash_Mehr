from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic
from pydantic import create_model
from typing import Optional

from src.core.util import set_password


class UserRoleEnum(StrEnum):
    Admin = "Admin"
    GroupAdmin = "GroupAdmin"


class Admin(Base):
    __tablename__ = "admin"
    AdminID: Mapped[int] = mapped_column(primary_key=True, index=True)
    FirstName: Mapped[str] = mapped_column(String(100), nullable=False)
    LastName: Mapped[str] = mapped_column(String(100), nullable=False)
    Phone: Mapped[Optional[str]] = mapped_column(String(20))
    PostCode: Mapped[Optional[str]] = mapped_column(String(20))
    Email: Mapped[Optional[str]] = mapped_column(String(100))
    City: Mapped[Optional[str]] = mapped_column(String(100))
    Province: Mapped[Optional[str]] = mapped_column(String(100))
    Street: Mapped[Optional[str]] = mapped_column(String(100))
    NationalID: Mapped[Optional[str]] = mapped_column(String(20))
    UserRole: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), default=UserRoleEnum.Admin)
    Password: Mapped[str] = mapped_column(String(128), nullable=False)
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    ### create __init__ method to create an admin
    def __init__(self, FirstName: str, LastName: str, Phone: str, Email: str, City: str, Province: str, Street: str, NationalID: str, UserRole: UserRoleEnum, Password: str, PostCode: str = None):
        self.PostCode = PostCode
        self.FirstName = FirstName
        self.LastName = LastName
        self.Phone = Phone
        self.Email = Email
        self.City = City
        self.Province = Province
        self.Street = Street
        self.NationalID = NationalID
        self.UserRole = UserRole
        self.Password = set_password(Password)

    ### create admin
    def create_admin(self, db_session):
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)
        return self

    ## delete admin
    def delete_admin(self, db_session):
        db_session.delete(self)
        db_session.commit()
        return self

AdminCreate = sqlalchemy_model_to_pydantic(Admin, exclude=['AdminID', 'CreatedDate', 'UpdatedDate'])
