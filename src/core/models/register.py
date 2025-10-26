from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, DateTime, Date, Boolean
from sqlalchemy.sql import func
from src.core.models import sqlalchemy_model_to_pydantic
from src.core.models import Base
from pydantic import field_validator


def info_register(db_session):
    total_needy_person = db_session.query(Register).count()
    last_needy_person = db_session.query(Register).order_by(Register.CreatedDate.desc()).first()
    return {
        "total_needy_person": total_needy_person,
        "last_needy_person": {
            last_needy_person.FirstName: last_needy_person.FirstName,
            last_needy_person.LastName: last_needy_person.LastName,
            last_needy_person.CreatedDate: last_needy_person.CreatedDate,
        } if last_needy_person else None
    }

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
    BirthDate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    UnderWhichAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("admin.AdminID"), nullable=True)
    UnderSecondAdminID: Mapped[Optional[int]] = mapped_column(ForeignKey("admin.AdminID"), nullable=True)
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
    Latitude: Mapped[Optional[str]] = mapped_column(Text)
    Longitude: Mapped[Optional[str]] = mapped_column(Text)
    is_disconnected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __init__(self, FirstName: Optional[str] = None, LastName: Optional[str] = None, Phone: Optional[str] = None, Email: Optional[str] = None, City: Optional[str] = None, Province: Optional[str] = None, Street: Optional[str] = None,
                 NameFather: Optional[str] = None, NationalID: Optional[str] = None, CreatedBy: Optional[int] = None, BirthDate: Optional[date] = None, UnderWhichAdmin: Optional[int] = None, Region: Optional[str] = None, Gender: Optional[str] = None,
                 HusbandFirstName: Optional[str] = None, HusbandLastName: Optional[str] = None, ReasonMissingHusband: Optional[str] = None, UnderOrganizationName: Optional[str] = None,
                 EducationLevel: Optional[str] = None, IncomeForm: Optional[str] = None, Latitude: Optional[str] = None, Longitude: Optional[str] = None, UnderSecondAdminID: Optional[int] = None , is_disconnected: Optional[bool] = False) -> None:
        self.FirstName = FirstName
        self.LastName = LastName
        self.Phone = Phone
        self.Email = Email
        self.City = City
        self.Province = Province
        self.Street = Street
        self.NationalID = NationalID
        self.CreatedBy = CreatedBy
        # Normalize BirthDate input (accepts date | str | "")
        if isinstance(BirthDate, str):
            _bd = BirthDate.strip()
            self.BirthDate = date.fromisoformat(_bd) if _bd else None
        else:
            self.BirthDate = BirthDate
        # Normalize UnderWhichAdmin input (accepts int | str | "")
        if isinstance(UnderWhichAdmin, str):
            _uwa = UnderWhichAdmin.strip()
            self.UnderWhichAdmin = int(_uwa) if _uwa else None
        else:
            self.UnderWhichAdmin = UnderWhichAdmin
        if isinstance(UnderSecondAdminID, str):
              _usa = UnderSecondAdminID.strip()
              self.UnderSecondAdminID = int(_usa) if _usa else None
        else:
              self.UnderSecondAdminID = UnderSecondAdminID
        self.Region = Region
        self.Gender = Gender
        self.HusbandFirstName = HusbandFirstName
        self.HusbandLastName = HusbandLastName
        self.ReasonMissingHusband = ReasonMissingHusband
        self.UnderOrganizationName = UnderOrganizationName
        self.EducationLevel = EducationLevel
        self.IncomeForm = IncomeForm
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.NameFather = NameFather
        self.is_disconnected = is_disconnected

    def create_register(self, db_session):
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)

        return self


    def edit_register(self, db_session, user_data):
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
        if user_data.CreatedBy is not None:
            self.CreatedBy = user_data.CreatedBy
        if getattr(user_data, 'BirthDate', None) is not None:
            bd = user_data.BirthDate
            if isinstance(bd, str):
                _bd = bd.strip()
                self.BirthDate = date.fromisoformat(_bd) if _bd else None
            else:
                self.BirthDate = bd
        if getattr(user_data, 'UnderWhichAdmin', None) is not None:
            uwa = user_data.UnderWhichAdmin
            if isinstance(uwa, str):
                _uwa = uwa.strip()
                self.UnderWhichAdmin = int(_uwa) if _uwa else None
            else:
                self.UnderWhichAdmin = uwa
            if getattr(user_data, 'UnderSecondAdminID', None) is not None:
                usa = user_data.UnderSecondAdminID
                if isinstance(usa, str):
                    _usa = usa.strip()
                    self.UnderSecondAdminID = int(_usa) if _usa else None
                else:
                    self.UnderSecondAdminID = usa
        if user_data.Region is not None:
            self.Region = user_data.Region
        if user_data.Gender is not None:
            self.Gender = user_data.Gender
        if user_data.HusbandFirstName is not None:
            self.HusbandFirstName = user_data.HusbandFirstName
        if user_data.HusbandLastName is not None:
            self.HusbandLastName = user_data.HusbandLastName
        if user_data.ReasonMissingHusband is not None:
            self.ReasonMissingHusband = user_data.ReasonMissingHusband
        if user_data.UnderOrganizationName is not None:
            self.UnderOrganizationName = user_data.UnderOrganizationName
        if user_data.EducationLevel is not None:
            self.EducationLevel = user_data.EducationLevel
        if user_data.IncomeForm is not None:
            self.IncomeForm = user_data.IncomeForm
        if user_data.Province is not None:
            self.Province = user_data.Province
        if user_data.NameFather is not None:
            self.NameFather = user_data.NameFather
        if user_data.Latitude is not None:
            self.Latitude = user_data.Latitude
        if user_data.Longitude is not None:
            self.Longitude = user_data.Longitude
        if user_data.is_disconnected is not None:
            self.is_disconnected = user_data.is_disconnected
        db_session.commit()
        db_session.refresh(self)
        return self


    def delete_register(self, db_session, register_id):
        childRegister: list[ChildrenOfRegister] = db_session.query(ChildrenOfRegister).filter(
            ChildrenOfRegister.RegisterID == register_id).all()
        for child in childRegister:
            db_session.delete(child)
        db_session.delete(self)
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

    def __init__(self, RegisterID: Optional[int] = None, Age: Optional[int] = None, Gender: Optional[str] = None, NationalID: Optional[int] = None, FirstName: Optional[str] = None, LastName: Optional[str] = None, EducationLevel: Optional[str] = None ):
        self.RegisterID = RegisterID
        self.Age = Age
        self.Gender = Gender
        self.NationalID = NationalID
        self.FirstName = FirstName
        self.LastName = LastName
        self.EducationLevel = EducationLevel

    def create_child_register(self, db_session):
         db_session.add(self)
         db_session.commit()
         db_session.refresh(self)

         return self

# --- Helpers for input normalization ---
def _normalize_digit_string(value: str) -> str:
    """
    Convert Persian/Arabic digits to Western digits.
    """
    if not isinstance(value, str):
        return value
    trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    return value.translate(trans)

## create RegisterCreate pydantic model with sqlalchemy_model_to_pydantic
RegisterCreate = sqlalchemy_model_to_pydantic(Register, exclude=['RegisterID', 'CreatedDate', 'UpdatedDate'])
ChildrenOfRegisterCreate = sqlalchemy_model_to_pydantic(ChildrenOfRegister, exclude=['CreatedDate', 'UpdatedDate'])

# Patched child model to sanitize Age
class ChildrenOfRegisterCreatePatched(ChildrenOfRegisterCreate):
    @field_validator('Age', mode='before')
    def _age_from_str(cls, v):
        if v in (None, '', 'null'):
            return None
        if isinstance(v, str):
            v_norm = _normalize_digit_string(v).strip()
            if v_norm == '':
                return None
            if v_norm.isdigit():
                return int(v_norm)
        return v

# Base for Register validators
class RegisterCreateBase(RegisterCreate):
    @field_validator('BirthDate', mode='before')
    def _birthdate_from_str(cls, v):
        if v in (None, '', 'null'):
            return None
        if isinstance(v, str):
            v_norm = _normalize_digit_string(v).strip()
            if not v_norm:
                return None
            try:
                return date.fromisoformat(v_norm)
            except ValueError:
                raise ValueError('BirthDate must be ISO format (YYYY-MM-DD)')
        return v

    @field_validator('UnderWhichAdmin', mode='before')
    def _under_admin_from_str(cls, v):
        if v in (None, '', 'null'):
            return None
        if isinstance(v, str):
            v_norm = _normalize_digit_string(v).strip()
            if v_norm == '':
                return None
            if v_norm.isdigit():
                return int(v_norm)
        return v


