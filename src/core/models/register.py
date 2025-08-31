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
    HusbandFirstName: Mapped[Optional[str]] = mapped_column()
    HusbandLastName: Mapped[Optional[str]] = mapped_column()
    ReasonMissingHusband: Mapped[Optional[str]] = mapped_column()
    UnderOrganizationName: Mapped[Optional[str]] = mapped_column()
    EducationLevel: Mapped[Optional[str]] = mapped_column()
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    IncomeForm: Mapped[Optional[str]] = mapped_column(Text)
    children_of_reg: Mapped[List["ChildrenOfRegister"]] = relationship("ChildrenOfRegister", back_populates="register")

    def __init__(self, FirstName: str, LastName: str, Phone: str, Email: str, City: str, Province: str, Street: str, NameFather: str, NationalID: str, CreatedBy: int, MessageID: int, Age: int, Region:str, Gender: str, HusbandFirstName: str,HusbandLastName: str, ReasonMissingHusband : str, UnderOrganizationName: str, EducationLevel: str, IncomeForm: str ):
        self.FirstName = FirstName
        self.LastName = LastName
        self.Phone = Phone
        self.Email = Email
        self.City = City
        self.Province = Province
        self.Street = Street
        self.NationalID = NationalID
        self.CreatedBy = CreatedBy
        self.MessageID = MessageID
        self.Age = Age
        self.Region = Region
        self.Gender = Gender
        self.HusbandFirstName = HusbandFirstName
        self.HusbandLastName = HusbandLastName
        self.ReasonMissingHusband = ReasonMissingHusband
        self.UnderOrganizationName = UnderOrganizationName
        self.EducationLevel = EducationLevel
        self.IncomeForm = IncomeForm

    def create_register(self, db_session):
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)
        children_data = self.__dict__.pop("children_of_reg", None)
        if children_data:
            for child in children_data:
                child_obj = ChildrenOfRegister(**child.dict(), RegisterID = self.RegisterID)
            db_session.add(child_obj)
            db_session.commit()
            db_session.refresh(child_obj)
        return self

    def edit_register(self, db_session, user_data):
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
        if user_data.CreatedBy:
            self.CreatedBy = user_data.CreatedBy
        if user_data.MessageID:
            self.MessageID = user_data.MessageID
        if user_data.Age:
            self.Age = user_data.Age
        if user_data.Region:
            self.Region = user_data.Region
        if user_data.Gender:
            self.Gender = user_data.Gender
        if user_data.HusbandFirstName:
            self.HusbandFirstName = user_data.HusbandFirstName
        if user_data.HusbandLastName:
            self.HusbandLastName = user_data.HusbandLastName
        if user_data.ReasonMissingHusband:
            self.ReasonMissingHusband = user_data.ReasonMissingHusband
        if user_data.UnderOrganizationName:
            self.UnderOrganizationName = user_data.UnderOrganizationName
        if user_data.EducationLevel:
            self.EducationLevel = user_data.EducationLevel
        if user_data.CreatedDate:
            self.CreatedDate = user_data.CreatedDate
        if user_data.UpdatedDate:
            self.UpdatedDate = user_data.UpdatedDate
        if user_data.IncomeForm:
            self.IncomeForm = user_data.IncomeForm


    def delete_register(self, db_session, register_id):
        db_session.delete(self)
        childRegister: list[ChildrenOfRegister] = db_session.query(ChildrenOfRegister).filter(
            ChildrenOfRegister.RegisterID == register_id).all()
        for child in childRegister:
            db_session.delete(child)
        db_session.commit()
        return self

class ChildrenOfRegister(Base):
    __tablename__ = "children_of_register"
    ChildrenOfRegisterID: Mapped[int] = mapped_column(primary_key=True, index=True)
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

    def __init__(self, RegisterID: int, Age: int, Gender: str, NationalID: int, FirstName: str, LastName: str, EducationLevel: str ):
        self.RegisterID = RegisterID
        self.Age = Age
        self.Gender = Gender
        self.NationalID = NationalID
        self.FirstName = FirstName
        self.LastName = LastName
        self.EducationLevel = EducationLevel

## create RegisterCreate pydantic model with sqlalchemy_model_to_pydantic
RegisterCreate = sqlalchemy_model_to_pydantic(Register, exclude=['RegisterID', 'CreatedDate', 'UpdatedDate'])
ChildrenOfRegisterCreate = sqlalchemy_model_to_pydantic(ChildrenOfRegister, exclude=['ChildrenOfRegisterID', 'CreatedDate', 'UpdatedDate'])
## add ChildrenOfRegisterCreate to RegisterCreate as list
RegisterCreateWithChildren = create_model(
    "RegisterCreateWithChildren",
    __base__=RegisterCreate,
    children_of_registre=(Optional[list[ChildrenOfRegisterCreate]], None)
)

