from datetime import datetime, timezone

from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.api import router
from src.config.database import create_session
from src.core.models.good import Good, GoodCreate, GoodUpsert


@router.get("/get-goods/{register_id}", status_code=201)
def get_good(
        register_id: int,
        db: Session = Depends(create_session)
):
    goods = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    return goods


@router.post("/edit-good/{register_id}")
def edit_good(
        register_id: int,
        user_data: List[GoodUpsert] | None = Body(None),
        db: Session = Depends(create_session)
):
    if user_data is None:
        raise HTTPException(status_code=400, detail="Payload لازم است")

    existing_goods = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    existing_by_id = {g.GoodID: g for g in existing_goods}

    received_ids: set[int] = set()
    now = datetime.now(timezone.utc)

    for item in user_data:
        data = item.model_dump(exclude_unset=True)
        good_id = data.get("GoodID")
        if isinstance(good_id, int) and good_id in existing_by_id:
            good_obj = existing_by_id[good_id]
            if "TypeGood" in data:
                good_obj.TypeGood = data["TypeGood"]
            if "NumberGood" in data and data["NumberGood"] is not None:
                good_obj.NumberGood = data["NumberGood"]
            if "GivenBy" in data and data["GivenBy"] is not None:
                good_obj.GivenBy = data["GivenBy"]
            good_obj.UpdatedDate = now
            received_ids.add(good_id)
        else:
            new_payload = {
                "TypeGood": data.get("TypeGood"),
                "NumberGood": data.get("NumberGood"),
                "GivenToWhome": register_id,
                "GivenBy": data.get("GivenBy"),
                "UpdatedDate": now,
            }
            new_good = Good(**new_payload)
            db.add(new_good)
            db.flush()
            received_ids.add(new_good.GoodID)

    to_delete = [g for g in existing_goods if g.GoodID not in received_ids]
    for g in to_delete:
        db.delete(g)

    db.commit()

    updated_goods = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    return updated_goods


