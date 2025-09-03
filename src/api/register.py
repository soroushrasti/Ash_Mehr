from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import func, literal
from src.api import router
from src.config.database import create_session
from src.core.models.register import Register, RegisterCreateWithChildren, RegisterCreate
from sqlalchemy import func, literal, case, cast, Float


class MapPoint(BaseModel):
    id: str
    lat: float
    lng: float
    name: Optional[str] = None
    info: Optional[str] = None


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
    register = db.query(Register).filter(Register.RegisterID == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Register not found")
    else:
        return register.edit_register(db, user_data)

@router.delete("/delete-register/{register_id}", status_code=200)
def delete_register(
        register_id: int,
        db: Session = Depends(create_session)
):
    register: Register = db.query(Register).filter(Register.RegisterID == register_id).first()
    return register.delete_register(db,register_id)

@router.get("/find-needy")
def find_needy(
        db: Session = Depends(create_session)
):
    bind = db.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    name_expr = func.nullif(
        func.trim(
            func.concat(
                func.coalesce(Register.FirstName, ""),
                literal(" "),
                func.coalesce(Register.LastName, ""),
            )
        ),
        "",
    ).label("name")

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
            name_expr,
            info_expr,
        )
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
    # rows is a list of dict-like mappings: {id, lat, lng, name, info}
    return rows

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
