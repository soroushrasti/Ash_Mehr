import bcrypt
from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy import func, literal, case, cast, Float

from src.api import router
from src.config.database import create_session
from src.core.models.admin import Admin, AdminCreate, AdminOut, UserRoleEnum


class AdminLogin(BaseModel):
    Username: str
    Password: str

# Map point response model for location endpoints
class MapPoint(BaseModel):
    id: str
    lat: float
    lng: float
    name: Optional[str] = None
    info: Optional[str] = None


@router.post("/signup-admin", status_code=201, response_model=AdminOut)
def signup_admin(
        user_data: AdminCreate = Body(...),
        db: Session = Depends(create_session)
):
    admin: Admin = Admin(**user_data.dict())
    return admin.create_admin(db)

## delete admin
@router.delete("/delete-admin/{admin_id}", status_code=200, response_model=AdminOut)
def delete_admin(
        admin_id: int,
        db: Session = Depends(create_session)
):
    admin: Admin = db.query(Admin).filter(Admin.AdminID == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin.delete_admin(db)

@router.post("/edit-admin/{admin_id}", response_model=AdminOut)
def edit_admin(
        admin_id: int,
        user_data: AdminCreate = Body(...),
        db: Session = Depends(create_session)
):
    admin :Admin = db.query(Admin).filter(Admin.AdminID == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    else:
        return admin.edit_admin(db_session=db, user_data=user_data)

@router.post("/login", status_code=200)
def login_admin(
        user_data: AdminLogin = Body(...),
        db: Session = Depends(create_session)
):
    admin: Admin = db.query(Admin).filter(Admin.Phone == user_data.Username).first()
    if not admin:
        ## error in farsi
        raise HTTPException(status_code=401, detail="شماره همراه اشتباه است")
    if user_data.Password != admin.Password:
        raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")
    name = f"{admin.FirstName or ''} {admin.LastName or ''}".strip() or None
    return {
        "adminID": admin.AdminID,
        "name": name,
        "userRole": admin.UserRole,
    }


@router.get("/info-admin")
def info_admin_stats(
        db: Session = Depends(create_session)
):
    counts = (
        db.query(
            func.coalesce(
                func.sum(case((Admin.UserRole == UserRoleEnum.GroupAdmin, 1), else_=0)), 0
            ).label("numberGroupAdminPersons"),
            func.coalesce(
                func.sum(case((Admin.UserRole == UserRoleEnum.Admin, 1), else_=0)), 0
            ).label("numberAdminPersons"),
        )
        .one()
    )

    last_admin = (
        db.query(Admin.FirstName, Admin.LastName, Admin.CreatedDate)
        .order_by(Admin.CreatedDate.desc())
        .filter(Admin.UserRole == UserRoleEnum.Admin)
        .limit(1)
        .first()
    )

    last_group_admin = (
        db.query(Admin.FirstName, Admin.LastName, Admin.CreatedDate)
        .order_by(Admin.CreatedDate.desc())
        .filter(Admin.UserRole == UserRoleEnum.GroupAdmin)
        .limit(1)
        .first()
    )

    last_name_admin = (
        " ".join([v for v in [last_admin.FirstName, last_admin.LastName] if v]).strip() if last_admin else None
    )

    last_name_group_admin = (
        " ".join([v for v in [last_group_admin.FirstName, last_group_admin.LastName] if v]).strip() if last_group_admin else None
    )

    return {
        "numberGroupAdminPersons": counts.numberGroupAdminPersons or 0,
        "numberAdminPersons": counts.numberAdminPersons or 0,
        "LastAdminCreatedTime": last_admin.CreatedDate if last_admin else None,
        "LastAdminNameCreated": last_name_admin or None,
        "LastGroupAdminCreatedTime": last_group_admin.CreatedDate if last_group_admin else None,
        "LastGroupAdminNameCreated": last_name_group_admin or None,
    }

@router.get("/admins", status_code=200, response_model=List[AdminOut])
def list_admins(
        db: Session = Depends(create_session)
):
    return db.query(Admin).all()

@router.get("/find-admin")
def find_admin(
        db: Session = Depends(create_session)
):
    bind = db.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    name_expr = func.nullif(
        func.trim(
            func.concat(
                func.coalesce(Admin.FirstName, ""),
                literal(" "),
                func.coalesce(Admin.LastName, ""),
            )
        ),
        "",
    ).label("name")

    info_expr = func.nullif(
        func.trim(
            func.concat(
                func.coalesce(Admin.Street, ""),
                literal(" "),
                func.coalesce(Admin.City, ""),
            )
        ),
        "",
    ).label("info")
    lat_expr = cast(func.trim(Admin.Latitude), Float).label("lat")
    lng_expr = cast(func.trim(Admin.Longitude), Float).label("lng")

    query = (
        db.query(
            Admin.AdminID.label("id"),
            lat_expr,
            lng_expr,
            name_expr,
            info_expr,
        )
        .filter(
            Admin.Latitude.isnot(None),
            Admin.Latitude != "",
            Admin.Longitude.isnot(None),
            Admin.Longitude != "",
        )
    )

    if is_pg:
        query = query.filter(
            Admin.Latitude.op("~")(r"^\s*[+-]?\d+(\.\d+)?\s*$"),
            Admin.Longitude.op("~")(r"^\s*[+-]?\d+(\.\d+)?\s*$"),
        )

    rows = db.execute(query.statement).mappings().all()
    return rows
