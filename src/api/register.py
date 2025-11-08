from datetime import datetime, timezone

from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Counter
from pydantic import BaseModel
from sqlalchemy import func, literal, cast, Float
from src.api import router
from src.config.database import create_session
from src.core.models.good import Good
from src.core.models.register import Register, RegisterCreate, ChildrenOfRegister, \
    ChildrenOfRegisterCreate
from src.core.models.admin import Admin
from src.objModel import RegisterCreateWithChildren


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
        normalized_user_phone = _normalize_digit_string(user_data.Phone)
        all_registers = db.query(Register).all()
        for register in all_registers:
            if register.Phone:
                normalized_db_phone = _normalize_digit_string(register.Phone)
                if normalized_user_phone == normalized_db_phone:
                    raise HTTPException(status_code=409, detail="مددجو با این شماره تلفن قبلا ثبت نام کرده است")

    payload = user_data.dict()
    children_data = payload.pop("children_of_registre", None)
    goods_data = payload.pop("goods_of_registre", None)

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

    if goods_data:
        ## get an admin_id
        admin_id = db.query(Admin.AdminID).first()[0]
        try:
            for good in goods_data:
                good["GivenToWhome"] = register.RegisterID
                good["UpdatedDate"] = datetime.now(timezone.utc)
                good["GivenBy"] = register.UnderWhichAdmin if register.UnderWhichAdmin else admin_id
                good_obj = Good(**good)
                db.add(good_obj)
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Error in goods registration: {str(e)}")  # Move print before raise
            raise HTTPException(status_code=500, detail=  "خطا در ثبت کمک ها")

    return register


@router.post("/signup-child-register", status_code= 201)
def signup_child_register(
        user_data: ChildrenOfRegisterCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    # حذف ChildrenOfRegisterID از payload اگر وجود دارد
    payload = user_data.dict(exclude_unset=True)

    # حذف explicit ChildrenOfRegisterID اگر به اشتباه ارسال شده
    payload.pop("ChildrenOfRegisterID", None)

    if "Age" in payload:
        age_val = payload.get("Age")
        if isinstance(age_val, str):
            norm = _normalize_digit_string(age_val).strip()
            if norm.isdigit():
                payload["Age"] = int(norm)
            elif norm == "":
                payload["Age"] = None

        register = ChildrenOfRegister(**payload)
        register = register.create_child_register(db)
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
            db.query(ChildrenOfRegister).filter(ChildrenOfRegister.ChildrenOfRegisterID == child["ChildrenOfRegisterID"]).update(child)

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
    db.query(Good).filter(Good.GivenToWhome == register_id).delete()
    db.query(ChildrenOfRegister).filter(ChildrenOfRegister.RegisterID == register_id).delete()
    db.query(Register).filter(Register.RegisterID == register_id).delete()
    db.commit()

@router.delete("/delete-child-needy/{register_id}", status_code=200)
def delete_child_register(
            register_id: int,
            db: Session = Depends(create_session)
    ):
        db.query(ChildrenOfRegister).filter(ChildrenOfRegister.ChildrenOfRegisterID == register_id).delete()
        db.commit()

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
            Register.is_disconnected == False
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

@router.get("/find-disconnected-needy")
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
            Register.is_disconnected == True
        )
    )

    if is_pg:
        # Filter numeric values using Postgres regex to avoid cast errors
        query = query.filter(
            Register.Latitude.op("~")(r"^\s*[+-]?\d+(\.\d+)?\s*$"),
            Register.Longitude.op("~")(r"^\s*[+-]?\d+(\.\d+)?\s*$"),
        )

    disconnected_rows = db.execute(query.statement).mappings().all()
    return disconnected_rows


# stattistic of needy people
@router.get("/info-needy")
def info_needy(
        db: Session = Depends(create_session)
):
    # Get total count of registers
    total_count = db.query(func.count(Register.RegisterID)).scalar() or 0

    # Get last created register
    last_register = (
        db.query(Register.FirstName, Register.LastName, Register.CreatedDate)
        .order_by(Register.CreatedDate.desc())
        .first()
    )

    if not last_register:
        return {
            "numberNeedyPersons": 0,
            "LastNeedycreatedTime": None,
            "LastNeedyNameCreated": None,
            "GoodId": None,
        }

    # Get last created good (if needed for this register)
    last_good = db.query(Good.GoodID).order_by(Good.CreatedDate.desc()).first()

    name = " ".join([v for v in [last_register.FirstName, last_register.LastName] if v]).strip() or None
    return {
        "numberNeedyPersons": total_count,
        "LastNeedycreatedTime": last_register.CreatedDate,
        "LastNeedyNameCreated": name,
        "GoodId": last_good.GoodID if last_good else None,
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


@router.get("/register-stats")
def register_stats(
        db: Session = Depends(create_session)
):
    # گرفتن تمام رجیسترها از دیتابیس
    registers = db.query(Register).all()

    # شمارش تعداد رجیسترها بر اساس admin name (not ID)
    admin_counts_query = (
        db.query(
            func.concat(
                func.coalesce(Admin.FirstName, ""),
                literal(" "),
                func.coalesce(Admin.LastName, "")
            ).label("admin_name"),
            func.count(Register.RegisterID).label("count")
        )
        .join(Admin, Register.UnderWhichAdmin == Admin.AdminID)
        .group_by(Admin.AdminID, Admin.FirstName, Admin.LastName)
        .all()
    )
    admin_counts = {row.admin_name.strip() or f"Admin {idx}": row.count for idx, row in enumerate(admin_counts_query, 1)}

    # شمارش تعداد رجیسترها بر اساس استان
    province_counts = Counter(register.Province for register in registers)
    # شمارش تعداد رجیسترها بر اساس سطح تحصیلات
    education_level_counts = Counter(register.EducationLevel for register in registers)

    # تعداد رجیسترها بر اساس TypeGood
    type_good_counts = dict(
        db.query(Good.TypeGood, func.count(Register.RegisterID))
        .join(Register, Good.GivenToWhome == Register.RegisterID)
        .group_by(Good.TypeGood)
        .all()
    )

    ## x  number of children counts unique until max children we have for a registerID 0,1,2,3,4
    ##  y number of register with that number of children

    # Subquery: count children per register
    children_per_register = (
        db.query(
            ChildrenOfRegister.RegisterID,
            func.count(ChildrenOfRegister.ChildrenOfRegisterID).label('child_count')
        )
        .group_by(ChildrenOfRegister.RegisterID)
        .subquery()
    )

    # Count how many registers have each number of children (including 0)
    # First get registers with children
    registers_with_children = dict(
        db.query(
            children_per_register.c.child_count,
            func.count(children_per_register.c.RegisterID)
        )
        .group_by(children_per_register.c.child_count)
        .all()
    )

    # Count registers with 0 children (not in children_of_register table)
    total_registers = db.query(func.count(Register.RegisterID)).scalar() or 0
    registers_with_children_count = db.query(func.count(func.distinct(ChildrenOfRegister.RegisterID))).scalar() or 0
    registers_with_zero_children = total_registers - registers_with_children_count

    # Combine: add 0 children count
    number_of_children_counts = {0: registers_with_zero_children}
    number_of_children_counts.update(registers_with_children)

    education_levels = [
        'Kindergarten',
        'Primary',
        'Secondary',
        'High School',
        'Diploma',
        'Associate Degree',
        'Bachelor',
        'Master',
        'PhD'
    ]

    # تبدیل به فرمت مناسب برای نمودار
    chart_data = {
        'adminStats': {
            'labels': list(admin_counts.keys()),
            'datasets': [{
                'label': 'تعداد رجیسترها بر اساس نماینده',
                'data': list(admin_counts.values()),
                'backgroundColor': '#4CAF50'
            }]
        },
        'provinceStats': {
            'labels': list(province_counts.keys()),
            'datasets': [{
                'label': 'تعداد رجیسترها بر اساس استان',
                'data': list(province_counts.values()),
                'backgroundColor': '#2196F3'
            }]
        },
        'educationLevelStats': {
            'labels': education_levels,
            'datasets': [{
                'label': 'تعداد رجیسترها بر اساس سطح تحصیلات',
                'data':  [education_level_counts.get(key, 0) for key in education_levels],
                'backgroundColor': '#2196F3'
            }]
        },
        'typeGoodStats': {
            'labels': list(type_good_counts.keys()),
            'datasets': [{
                'label': 'تعداد رجیسترها بر اساس نوع کمک',
                'data': list(type_good_counts.values()),
                'backgroundColor': '#9C27B0'
            }]
        },
        'childrenNumberStats': {
            'labels': list(number_of_children_counts.keys()),
            'datasets': [{
                'label': 'تعداد رجیسترها بر اساس تعداد فرزندان',
                'data': list(number_of_children_counts.values()),
                'backgroundColor': '#9C27B0'
            }]
        }
    }

    return chart_data
