from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api import router
from src.config.database import create_session
from src.core.models.message import Message, MessageCreate


@router.post("/add-message", status_code=201)
def add_message(
        user_data: MessageCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    payload = user_data.dict() if user_data else {}
    message = Message(**payload)
    return message.create_message(db)

@router.post("/edit-message/{message_id}")
def edit_message(
        message_id: int,
        user_data: MessageCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    message :Message = db.query(Message).filter(Message.MessageID == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="پیغام پیدا نشد")
    else:
        return message.edit_message(db_session=db, user_data= user_data or MessageCreate())
