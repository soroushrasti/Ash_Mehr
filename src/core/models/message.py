from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from src.core.models import Base, sqlalchemy_model_to_pydantic
from typing import Optional


class Message(Base):
    __tablename__ = "message"
    MessageID = Column(Integer, primary_key=True, index=True)
    MessageText = Column(Text)
    CreatedDate = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedDate = Column(DateTime(timezone=True), onupdate=func.now())
    ## created by whome
    CreatedBy = Column(Integer, ForeignKey("admin.AdminID"))
    ## give to whome
    GivenToWhome = Column(Integer, ForeignKey("register.RegisterID"))

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
        if getattr(user_data, 'CreatedDate', None) is not None:
            self.CreatedDate = user_data.CreatedDate
        if getattr(user_data, 'UpdatedDate', None) is not None:
            self.UpdatedDate = user_data.UpdatedDate
        if user_data.CreatedBy is not None:
            self.CreatedBy = user_data.CreatedBy
        if user_data.GivenToWhome is not None:
            self.GivenToWhome = user_data.GivenToWhome
        db_session.commit()
        return self

MessageCreate = sqlalchemy_model_to_pydantic(Message, exclude=['MessageID', 'CreatedDate', 'UpdatedDate'])
