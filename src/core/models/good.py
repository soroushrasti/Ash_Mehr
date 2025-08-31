from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic
from src.core.models.register import Register
from src.core.models.admin import Admin
from datetime import datetime

class Good(Base):
    __tablename__ = "good"
    GoodID: Mapped[int] = mapped_column(primary_key=True, index=True)
    TypeGood: Mapped[str] = mapped_column(String, index=True)
    NumberGood: Mapped[int] = mapped_column(Integer)
    GivenToWhome: Mapped[int] = mapped_column(ForeignKey("register.RegisterID"))
    GivenBy: Mapped[int] = mapped_column(ForeignKey("admin.AdminID"))
    CreatedDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships (optional, for ORM navigation)
    register: Mapped[Register] = relationship("Register")
    admin: Mapped[Admin] = relationship("Admin")

    ### create __init__ method to create an good
    def __init__(self, TypeGood: str, NumberGood: int, GivenToWhome: int, GivenBy: int = None):
        self.TypeGood = TypeGood
        self.NumberGood = NumberGood
        self.GivenToWhome = GivenToWhome
        self.GivenBy = GivenBy

    def create_good(self, db_session):
         db_session.add(self)
         db_session.commit()
         db_session.refresh(self)
         return self

    def edit_good(self, db_session, user_data):
        if user_data.TypeGood:
            self.TypeGood = user_data.TypeGood
        if user_data.NumberGood:
            self.NumberGood = user_data.NumberGood
        if user_data.GivenToWhome:
            self.GivenToWhome = user_data.GivenToWhome
        if user_data.GivenBy:
            self.GivenBy = user_data.GivenBy
        if user_data.CreatedDate:
            self.CreatedDate = user_data.CreatedDate
        if user_data.UpdatedDate:
            self.UpdatedDate = user_data.UpdatedDate
        db_session.commit()
        return self

GoodCreate = sqlalchemy_model_to_pydantic(Good, exclude=['GoodID', 'CreatedDate', 'UpdatedDate'])
