from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.core.models import Base
from src.core.models.register import Register
from src.core.models.admin import Admin


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
