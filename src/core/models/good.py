from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic, sqlalchemy_model_to_pydantic_named
from datetime import datetime
from typing import Optional
from pydantic import field_validator

from src.core.models.admin import Admin
from src.core.models.register import Register

class Good(Base):
    __tablename__ = "good"
    GoodID: Mapped[int] = mapped_column(primary_key=True, index=True)
    TypeGood: Mapped[str] = mapped_column(String, index=True)
    NumberGood: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    GivenToWhome: Mapped[int] = mapped_column(ForeignKey("register.RegisterID"))
    GivenBy: Mapped[int] = mapped_column(ForeignKey("admin.AdminID"))
    CreatedDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[datetime] = mapped_column(DateTime(timezone=True),  server_default=func.now(),onupdate=func.now())
    # Relationships (optional, for ORM navigation)
    admin: Mapped[Admin] = relationship("Admin")
    register: Mapped[Register] = relationship("Register")
    SmsCode : Mapped[Optional[str]] = mapped_column(String, index=True)
    Verified: Mapped[Optional[bool]] = mapped_column(Boolean, index=True, default=False)

    ### create __init__ method to create an good
    def __init__(self, TypeGood: Optional[str] = None, NumberGood: Optional[int] = None, GivenToWhome: Optional[int] = None, GivenBy: Optional[int] = None, UpdatedDate: Optional[datetime] = None, SmsCode: Optional[str] = None, Verified: Optional[bool] = None):
        self.TypeGood = TypeGood
        self.UpdatedDate = UpdatedDate
        if isinstance(NumberGood, str):
            _ng = NumberGood.strip()
            try:
                self.NumberGood = int(_ng) if _ng else None
            except ValueError:
                self.NumberGood = None
        else:
            self.NumberGood = NumberGood
        if isinstance(GivenToWhome, str):
            _gt = GivenToWhome.strip()
            self.GivenToWhome = int(_gt) if _gt else None
        else:
            self.GivenToWhome = GivenToWhome
        if isinstance(GivenBy, str):
            _gb = GivenBy.strip()
            self.GivenBy = int(_gb) if _gb else None
        else:
            self.GivenBy = GivenBy
        if SmsCode:
            self.SmsCode = SmsCode
        if Verified:
            self.Verified = Verified

    def edit_good(self, db_session, user_data):
        if user_data.TypeGood is not None:
            self.TypeGood = user_data.TypeGood
        if user_data.NumberGood is not None:
            self.NumberGood = user_data.NumberGood
        if user_data.GivenToWhome is not None:
            self.GivenToWhome = user_data.GivenToWhome
        if user_data.GivenBy is not None:
            self.GivenBy = user_data.GivenBy
        if user_data.SmsCode is not None:
            self.SmsCode = user_data.SmsCode
        if user_data.verified is not None:
            self.Verified = user_data.Verified
        db_session.commit()
        db_session.refresh(self)
        return self

GoodCreate = sqlalchemy_model_to_pydantic(Good, exclude=['GoodID', 'CreatedDate'])
GoodUpsert = sqlalchemy_model_to_pydantic_named(Good, "GoodUpsert", exclude=['CreatedDate'])

class GoodCreateFlexible(GoodCreate):
    NumberGood: int | str | None = None

    @field_validator("NumberGood", mode="before")
    @classmethod
    def normalize_number_good(cls, v):
        if v is None:
            return v
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # Normalize Persian/Arabic digits to ASCII
            trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
            cleaned = v.translate(trans).strip()
            if cleaned.isdigit():
                try:
                    return int(cleaned)
                except ValueError:
                    return None
            return None
        return None

class GoodUpsertFlexible(GoodUpsert):
    NumberGood: int | str | None = None

    @field_validator("NumberGood", mode="before")
    @classmethod
    def normalize_number_good(cls, v):
        if v is None:
            return v
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # Normalize Persian/Arabic digits to ASCII
            trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
            cleaned = v.translate(trans).strip()
            if cleaned.isdigit():
                try:
                    return int(cleaned)
                except ValueError:
                    return None
            return None
        return None
