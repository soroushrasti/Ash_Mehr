from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.api import router
from src.config.database import create_session
from src.core.models.good import Good, GoodCreate


@router.get("/get-goods/{register_id}", status_code=201)
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
    goods: List[Good] = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    if not goods:
        raise HTTPException(status_code=404, detail="کالا پیدا نشد")
    for good in goods:
         db.query(Good).filter(Good.GoodID == good.GoodID).delete()
    db.commit()
    payload = user_data.dict()
    payload['GivenToWhome'] = register_id
    for good in payload:
        newGood = Good(**good)
        db.add(newGood)
    db.commit()

    return [newGood]

@router.post("/add-good")
def add_good(
        user_data: GoodCreate | None = Body(None),
        db: Session = Depends(create_session)
):
    payload = user_data.dict()
    payload["UpdatedDate"] = datetime.now(timezone.utc)
    good = Good(**payload)
    db.add(good)
    db.commit()
    return good