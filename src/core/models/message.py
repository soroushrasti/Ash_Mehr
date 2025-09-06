from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic
from typing import Optional
from sqlalchemy.orm import Mapped
from datetime import datetime


class Message(Base):
    __tablename__ = "message"
    MessageID: Mapped[int]= Column(Integer, primary_key=True, index=True)
    MessageText : Mapped[str] = Column(Text)
    CreatedDate: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate: Mapped[datetime] = Column(DateTime(timezone=True), onupdate=func.now())
    ## created by whome
    CreatedBy: Mapped[int] = Column(Integer, ForeignKey("admin.AdminID"))
    ## give to whome
    GivenToWhome: Mapped[int] = Column(Integer, ForeignKey("register.RegisterID"))

    ### create __init__ method to create an message
    def __init__(self, MessageText: Optional[str] = None, CreatedBy: Optional[int] = None, GivenToWhome: Optional[int] = None):
        self.MessageText = MessageText
        self.CreatedBy = CreatedBy
        self.GivenToWhome = GivenToWhome

    def create_message(self, db_session):
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)
        return self

    def edit_message(self, db_session, user_data):
        if user_data.MessageText is not None:
            self.MessageText = user_data.MessageText
        if user_data.CreatedBy is not None:
            self.CreatedBy = user_data.CreatedBy
        if user_data.GivenToWhome is not None:
            self.GivenToWhome = user_data.GivenToWhome
        db_session.commit()
        db_session.refresh(self)
        return self

MessageCreate = sqlalchemy_model_to_pydantic(Message, exclude=['MessageID', 'CreatedDate', 'UpdatedDate'])
