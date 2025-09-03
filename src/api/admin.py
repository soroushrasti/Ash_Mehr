from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api import router
from src.config.database import create_session
from src.core.models.admin import Admin, AdminCreate, AdminOut


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
        return admin.edit_admin(db_session=db, user_data=user_data)
