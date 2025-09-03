from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api import router
from src.config.database import create_session
from src.core.models.register import Register, RegisterCreateWithChildren, RegisterCreate


@router.post("/signup-register", status_code=201)
def signup_register(
        user_data: RegisterCreateWithChildren = Body(...),
        db: Session = Depends(create_session)
):
    register = Register(**user_data.dict())
    return register.create_register(db)


@router.post("/edit-register/{register_id}")
def edit_register(
        register_id: int,
        user_data: RegisterCreate = Body(...),
        db: Session = Depends(create_session)
):
    register = db.query(Register).filter(Register.ResisterID == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Register not found")
    else:
        return register.edit_register(db, user_data)

@router.delete("/delete-register/{register_id}", status_code=200)
def delete_register(
        register_id: int,
        db: Session = Depends(create_session)
):
    register = db.query(Register).filter(Register.RegisterID == register_id).first()
    return register.delete_register(db,register_id)

@router.post("/find-register")
def find_register(
        user_data: Register = Body(...),
        db: Session = Depends(create_session)
):
    register = Register(**user_data.dict())
    return register.find_register(db)

@router.get("/info_needy")
def info_needy(
    user_data: Register = Body(...),
    db: Session = Depends(create_session)
):
    return  user_data.info_needy(db)

@router.get("/find-needy")
def find_needy(
        user_data: Register = Body(...),
        db: Session = Depends(create_session)
):
    return user_data.find_needy(db)
