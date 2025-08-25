from fastapi import  Body, Depends
from sqlalchemy.orm import Session

from src.api import router
from src.config.database import create_session
from src.core.models.register import Register,RegisterCreateWithChildren


@router.post("/signup-register", status_code=201)
def signup_register(
        user_data: RegisterCreateWithChildren = Body(...),
        db: Session = Depends(create_session)
):
    register = Register(**user_data.dict())
    return register.create(db)