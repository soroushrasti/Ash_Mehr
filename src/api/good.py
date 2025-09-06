from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api import router
from src.config.database import create_session
from src.core.models.good import Good, GoodCreate


@router.post("/add-good", status_code=201)
def add_good(
        user_data: GoodCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    payload = user_data.dict() if user_data else {}
    good = Good(**payload)
    return good.create_good(db)

@router.post("/edit-good/{good_id}")
def edit_good(
        good_id: int,
        user_data: GoodCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    good :Good = db.query(Good).filter(Good.GoodID == good_id).first()
    if not good:
        raise HTTPException(status_code=404, detail="کالا پیدا نشد")
    else:
        return good.edit_good(db_session=db, user_data=user_data or GoodCreate())
