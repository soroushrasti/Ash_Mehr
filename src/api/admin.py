from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

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
