from datetime import datetime
from enum import StrEnum

from sqlalchemy import String, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic, sqlalchemy_model_to_pydantic_named
from typing import Optional



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
    Latitude: Mapped[Optional[str]] = mapped_column(Text)
    Longitude: Mapped[Optional[str]] = mapped_column(Text)

    def __init__(self, FirstName: Optional[str] = None, LastName: Optional[str] = None, Phone: Optional[str] = None, Email: Optional[str] = None, City: Optional[str] = None, Province: Optional[str] = None, Street: Optional[str] = None, NationalID: Optional[str] = None, UserRole: Optional[UserRoleEnum] = None, Password: Optional[str] = None, PostCode: Optional[str] = None, Latitude: Optional[str] = None, Longitude: Optional[str] = None):
        self.PostCode = PostCode
        self.FirstName = FirstName
        self.LastName = LastName
        self.Phone = Phone
        self.Email = Email
        self.City = City
        self.Province = Province
        self.Street = Street
        self.NationalID = NationalID
        self.UserRole = UserRole or UserRoleEnum.Admin
        self.Password = Password
        self.Latitude = Latitude
        self.Longitude = Longitude

    def create_admin(self, db_session):
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)
        return self

    def delete_admin(self, db_session):
        db_session.delete(self)
        db_session.commit()
        return self

    def edit_admin(self, db_session, user_data: 'AdminCreate'):
        if user_data.FirstName is not None:
            self.FirstName = user_data.FirstName
        if user_data.LastName is not None:
            self.LastName = user_data.LastName
        if user_data.Phone is not None:
            self.Phone = user_data.Phone
        if user_data.Email is not None:
            self.Email = user_data.Email
        if user_data.City is not None:
            self.City = user_data.City
        if user_data.Province is not None:
            self.Province = user_data.Province
        if user_data.Street is not None:
            self.Street = user_data.Street
        if user_data.NationalID is not None:
            self.NationalID = user_data.NationalID
        if user_data.UserRole is not None:
            self.UserRole = user_data.UserRole
        if user_data.Password is not None:
            self.Password = user_data.Password
        if user_data.PostCode is not None:
            self.PostCode = user_data.PostCode
        if user_data.CreatedDate is not None:
            self.CreatedDate = user_data.CreatedDate
        if user_data.UpdatedDate is not None:
            self.UpdatedDate = user_data.UpdatedDate
        if user_data.Latitude is not None:
            self.Latitude = user_data.Latitude
        if user_data.Longitude is not None:
            self.Longitude = user_data.Longitude
        db_session.commit()
        db_session.refresh(self)
        return self

AdminCreate = sqlalchemy_model_to_pydantic(Admin, exclude=['AdminID', 'CreatedDate', 'UpdatedDate'])
AdminOut = sqlalchemy_model_to_pydantic_named(Admin, "AdminOut", exclude=["Password"])
