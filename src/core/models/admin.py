from datetime import datetime
from enum import StrEnum

import bcrypt
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic, sqlalchemy_model_to_pydantic_named
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
    Latitude: Mapped[Optional[str]] = mapped_column(Text)
    Longitude: Mapped[Optional[str]] = mapped_column(Text)

    ### create __init__ method to create an admin
    def __init__(self, FirstName: str, LastName: str, Phone: str, Email: str, City: str, Province: str, Street: str, NationalID: str, UserRole: UserRoleEnum, Password: str, PostCode: str = None, Latitude: str = None, Longitude: str = None):
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
        self.Latitude = Latitude
        self.Longitude = Longitude

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

    ## edit admin
    def edit_admin(self, db_session, user_data):
        if user_data.FirstName:
            self.FirstName = user_data.FirstName
        if user_data.LastName:
            self.LastName = user_data.LastName
        if user_data.Phone:
            self.Phone = user_data.Phone
        if user_data.Email:
            self.Email = user_data.Email
        if user_data.City:
            self.City = user_data.City
        if user_data.Province:
            self.Province = user_data.Province
        if user_data.Street:
            self.Street = user_data.Street
        if user_data.NationalID:
            self.NationalID = user_data.NationalID
        if user_data.UserRole:
            self.UserRole = user_data.UserRole
        if user_data.Password:
            self.Password = user_data.Password
        if user_data.PostCode:
            self.PostCode = user_data.PostCode
        if user_data.CreatedDate:
            self.CreatedDate = user_data.CreatedDate
        if user_data.UpdatedDate:
            self.UpdatedDate = user_data.UpdatedDate
        db_session.commit()
        db_session.refresh(self)
        return self

    def info_admin(self, db_session):
        total_admin = db_session.query(Admin).filter(Admin.UserRole == UserRoleEnum.Admin).count()
        total_group_admin = db_session.query(Admin).filter(Admin.UserRole == UserRoleEnum.GroupAdmin).count()
        last_admin = db_session.query(Admin).order_by(Admin.CreatedDate.desc()).first()
        return {
            "total_admin": total_admin,
            "total_group_admin": total_group_admin,
            "last_admin": {
                last_admin.FirstName,
                last_admin.LastName,
                last_admin.CreatedDate,
            } if last_admin else None
        }

    def find_admin(self, db_session):
        result_list = db_session.query(Admin).filter(Admin.Latitude.isnot(None), Admin.Longitude.isnot(None)).all()
        needy_list = [(row.AdminID, row.Latitude, row.Longitude, row.FirstName, row.LastName, row.City, row.Street) for row in result_list]
        return needy_list

AdminCreate = sqlalchemy_model_to_pydantic(Admin, exclude=['AdminID', 'CreatedDate', 'UpdatedDate'])
# New response model excluding sensitive Password
AdminOut = sqlalchemy_model_to_pydantic_named(Admin, "AdminOut", exclude=["Password"])
