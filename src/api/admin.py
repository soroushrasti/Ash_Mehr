from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from src.api import router
from src.config.database import create_session
from src.core.models.admin import Admin, AdminCreate


@router.post("/signup-admin", status_code=201)
def signup_admin(
        user_data: AdminCreate = Body(...),
        db: Session = Depends(create_session)
):
    admin = Admin(**user_data.dict())
    return admin.create_admin(db)

## delete admin
@router.delete("/delete-admin/{admin_id}", status_code=200)
def delete_admin(
        admin_id: int,
        db: Session = Depends(create_session)
):
    admin = db.query(Admin).filter(Admin.AdminID == admin_id).first()
    return admin.delete_admin(db)

@router.post("/edit-admin/{admin_id}")
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
    try:
        admin = db.query(Admin).filter(Admin.Email == user_data.Email).first()
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid admin")
        return admin.login_admin(db, user_data.Email, user_data.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error logging in: {str(e)}"
        )


