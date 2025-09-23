from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import func, literal, cast, Float
from src.api import router
from src.config.database import create_session
from src.core.models.register import Register, RegisterCreateWithChildren, RegisterCreate, ChildrenOfRegister
from src.core.models.admin import Admin


class MapPoint(BaseModel):
    id: str
    lat: float
    lng: float
    name: Optional[str] = None
    info: Optional[str] = None


def _normalize_digit_string(value: str):
    if not isinstance(value, str):
        return value
    return value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))


@router.post("/signup-register", status_code=201)
def signup_register(
        user_data: RegisterCreateWithChildren | None = Body(None),
        db: Session = Depends(create_session)
):
    if not user_data:
        raise HTTPException(status_code=400, detail="Payload required")
    if user_data.Phone is not None and user_data.Phone != "":
        rregister: Register = db.query(Register).filter(Register.Phone == user_data.Phone).first()
        if rregister is not None:
            raise HTTPException(status_code=409, detail="مددجو با این شماره تلفن قبلا ثبت نام کرده است")

    payload = user_data.dict()
    children_data = payload.pop("children_of_registre", None)

    # 1. Create parent first (use existing helper method for consistency)
    register = Register(**payload)
    register = register.create_register(db)  # assumes this commits & refreshes

    # 2. Now persist children with correct FK
    if children_data:
        try:
            for child in children_data:
                # Remove any incoming incorrect keys
                child.pop("ChildrenOfRegisterID", None)
                child["RegisterID"] = register.RegisterID  # enforce FK
                # Normalize Age (Persian digits -> int or None)
                if "Age" in child:
                    age_val = child.get("Age")
                    if isinstance(age_val, str):
                        norm = _normalize_digit_string(age_val).strip()
                        if norm.isdigit():
                            child["Age"] = int(norm)
                        elif norm == "":
                            child["Age"] = None
                child_obj = ChildrenOfRegister(**child)
                db.add(child_obj)
            db.commit()
        except Exception:
            db.rollback()
            # Optional: could also delete the parent if atomicity across parent/children is required
            raise HTTPException(status_code=500, detail="خطا در ثبت فرزندان")

    return register

@router.post("/edit-needy/{register_id}")
def edit_register(
        register_id: int,
        user_data: RegisterCreateWithChildren | None = Body(None),
        db: Session = Depends(create_session)
):
    payload = user_data.dict()
    children_data = payload.pop("children_of_registre", None)
    if children_data:
        for child in children_data:
            db.query(ChildrenOfRegister).filter(ChildrenOfRegister.ChildrenOfRegisterID == child["RegisterID"]).update(child)

    register: Register = db.query(Register).filter(Register.RegisterID == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="مدد جو پیدا نشد")
    else:
        return register.edit_register(db_session=db, user_data=user_data or RegisterCreate())


@router.delete("/delete-needy/{register_id}", status_code=200)
def delete_register(
        register_id: int,
        db: Session = Depends(create_session)
):
    # first delete children
    db.query(ChildrenOfRegister).filter(ChildrenOfRegister.RegisterID == register_id).delete()
    db.query(Register).filter(Register.RegisterID == register_id).delete()

## find needy people with lat and lng
@router.get("/find-needy")
def find_needy(
        db: Session = Depends(create_session)
):
    bind = db.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    needy_name_expr = func.nullif(
        func.trim(
            func.concat(
                func.coalesce(Register.FirstName, ""),
                literal(" "),
                func.coalesce(Register.LastName, ""),
            )
        ),
        "",
    ).label("name")

    group_name_expr = func.nullif(
        func.trim(
            func.concat(
                func.coalesce(Admin.FirstName, ""),
                literal(" "),
                func.coalesce(Admin.LastName, ""),
                literal(" "),
                func.coalesce(Admin.City, ""),
            )
        ),
        "",
    ).label("group_name")

    info_expr = func.nullif(
        func.trim(
            func.concat(
                func.coalesce(Register.Street, ""),
                literal(" "),
                func.coalesce(Register.City, ""),
            )
        ),
        "",
    ).label("info")

    lat_expr = cast(func.trim(Register.Latitude), Float).label("lat")
    lng_expr = cast(func.trim(Register.Longitude), Float).label("lng")

    query = (
        db.query(
            Register.RegisterID.label("id"),
            lat_expr,
            lng_expr,
            needy_name_expr,
            group_name_expr,
            info_expr,
            Register.Phone.label('phone')
        ).join(Admin, Admin.AdminID == Register.UnderWhichAdmin, isouter=True)
        .filter(
            Register.Latitude.isnot(None),
            Register.Latitude != "",
            Register.Longitude.isnot(None),
            Register.Longitude != "",
        )
    )

    if is_pg:
        # Filter numeric values using Postgres regex to avoid cast errors
        query = query.filter(
            Register.Latitude.op("~")(r"^\s*[+-]?\d+(\.\d+)?\s*$"),
            Register.Longitude.op("~")(r"^\s*[+-]?\d+(\.\d+)?\s*$"),
        )

    rows = db.execute(query.statement).mappings().all()
    return rows

# stattistic of needy people
@router.get("/info-needy")
def info_needy(
        db: Session = Depends(create_session)
):
    top = (
        db.query(
            func.count().over().label("total"),
            Register.FirstName,
            Register.LastName,
            Register.CreatedDate,
        )
        .order_by(Register.CreatedDate.desc())
        .limit(1)
        .first()
    )

    if not top:
        return {
            "numberNeedyPersons": 0,
            "LastNeedycreatedTime": None,
            "LastNeedyNameCreated": None,
        }

    name = " ".join([v for v in [top.FirstName, top.LastName] if v]).strip() or None
    return {
        "numberNeedyPersons": top.total,
        "LastNeedycreatedTime": top.CreatedDate,
        "LastNeedyNameCreated": name,
    }

@ router.get("/get-needy/{register_id}")
def get_needy(
        register_id: int,
        db: Session = Depends(create_session)
):
    needy: Register = db.query(Register).filter(Register.RegisterID == register_id).first()
    if not needy:
        raise HTTPException(status_code=404, detail="مددجو یافت نشد")

    childNeedy: List[ChildrenOfRegister] = db.query(ChildrenOfRegister).filter(ChildrenOfRegister.RegisterID == register_id).all()
    children_list = [child.__dict__ for child in childNeedy]

    for child in children_list:
        child.pop('_sa_instance_state', None)

    return {
        **needy.__dict__,
        'children': children_list
        }

@router.post("/signin-needy", status_code=201)
def signin_needy(
        user_data: RegisterCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    needy: Register = db.query(Register).filter(Register.Phone == user_data.Phone).first()
    if not needy:
        raise HTTPException(status_code=404, detail="شماره تلفن پیدا نشد")
    name = f"{needy.FirstName or ''} {needy.LastName or ''}".strip() or None
    return {
        "needyID": needy.RegisterID,
        "name": name,
    }
