import bcrypt
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from src.api import router
from src.config.database import create_session
from src.core.models.admin import Admin, AdminCreate, AdminOut, UserRoleEnum


@router.post("/signup-admin", status_code=201, response_model=AdminOut)
def signup_admin(
        user_data: AdminCreate = Body(...),
        db: Session = Depends(create_session)
):
    admin = Admin(**user_data.dict())
    return admin.create_admin(db)

## delete admin
@router.delete("/delete-admin/{admin_id}", status_code=200, response_model=AdminOut)
def delete_admin(
        admin_id: int,
        db: Session = Depends(create_session)
):
    admin = db.query(Admin).filter(Admin.AdminID == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin.delete_admin(db)

@router.post("/edit-admin/{admin_id}", response_model=AdminOut)
def edit_admin(
        admin_id: int,
        user_data: AdminCreate = Body(...),
        db: Session = Depends(create_session)
):
    admin = db.query(Admin).filter(Admin.AdminID == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    else:
        return admin.edit_admin(db, user_data)

@router.post("login-admin", status_code=200)
def login_admin(
        user_data: AdminCreate = Body(...),
        db: Session = Depends(create_session)
):
        admin = db.query(Admin).filter(Admin.Email == user_data.Email).first()
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid admin")
        else:
            checkpassword = bcrypt.checkpw(admin.Password.encode('utf-8'), user_data.Password.encode('utf-8'))
            if not checkpassword:
                raise HTTPException(status_code=401, detail="Invalid password")
        return  admin


@router.get("info_admin", status_code=200)
def info_admin(
        user_data: Admin = Body(...),
        db: Session = Depends(create_session)
):
    return user_data.info_admin(db)

@router.get("/find-admin")
def find_admin(
        user_data: Admin = Body(...),
        db: Session = Depends(create_session)
):
    return user_data.find_admin(db)

