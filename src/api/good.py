from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.api import router
from src.config.database import create_session
from src.core.models.good import Good, GoodCreate


@router.post("/get-goods/{register_id}", status_code=201)
def get_good(
        register_id: int,
        db: Session = Depends(create_session)
):
    goods: List[Good] = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    return goods


@router.post("/edit-good/{register_id}")
def edit_good(
        register_id: int,
        user_data: GoodCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    goods : List[Good] = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    if not goods:
        raise HTTPException(status_code=404, detail="کالا پیدا نشد")
    else:
        for good in goods:
            db.query(Good).filter(Good.GoodID == good.GoodID).delete()
            good.edit_good(db_session=db, user_data=user_data or GoodCreate())
    return goods
