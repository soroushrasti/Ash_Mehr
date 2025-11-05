from datetime import datetime, timezone
import random
import requests
import json
from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from pydantic import BaseModel, field_validator
from src.api import router
from src.config.database import create_session
from src.core.models.good import Good

# Strict input models enforcing required NumberGood as integer
class _GoodNumberMixin(BaseModel):
    TypeGood: str
    NumberGood: int | str
    GivenBy: int | str | None = None

    @field_validator("NumberGood", mode="before")
    @classmethod
    def validate_number_good(cls, v):
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
            cleaned = v.translate(trans).strip()
            if cleaned.isdigit():
                return int(cleaned)
        raise ValueError("NumberGood must be an integer")

    @field_validator("GivenBy", mode="before")
    @classmethod
    def validate_given_by(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            if v.strip().isdigit():
                return int(v.strip())
        raise ValueError("GivenBy must be an integer or null")

class GoodEditItem(_GoodNumberMixin):
    GoodID: int | None = None

class GoodCreateStrict(_GoodNumberMixin):
    pass

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
        user_data: Union[GoodEditItem, List[GoodEditItem]] | None = Body(None),
        db: Session = Depends(create_session)
):
    if user_data is None:
        raise HTTPException(status_code=400, detail="Payload لازم است")

    # Normalize to list
    if isinstance(user_data, GoodEditItem):
        items: List[GoodEditItem] = [user_data]
    else:
        items = list(user_data)
    if len(items) == 0:
        return []

    existing_goods = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    existing_by_id = {g.GoodID: g for g in existing_goods}

    received_ids: set[int] = set()
    now = datetime.now(timezone.utc)

    for item in items:
        good_id = item.GoodID
        if isinstance(good_id, int) and good_id in existing_by_id:
            good_obj = existing_by_id[good_id]
            good_obj.TypeGood = item.TypeGood
            good_obj.NumberGood = item.NumberGood  # already validated int
            if item.GivenBy is not None:
                good_obj.GivenBy = item.GivenBy
            good_obj.UpdatedDate = now
            received_ids.add(good_id)
        else:
            new_good = Good(
                TypeGood=item.TypeGood,
                NumberGood=item.NumberGood,
                GivenToWhome=register_id,
                GivenBy=item.GivenBy,
                UpdatedDate=now,
            )
            db.add(new_good)
            db.flush()
            received_ids.add(new_good.GoodID)

    # Delete goods not present in payload
    to_delete = [g for g in existing_goods if g.GoodID not in received_ids]
    for g in to_delete:
        db.delete(g)

    db.commit()

    updated_goods = db.query(Good).filter(Good.GivenToWhome == register_id).all()
    return updated_goods


@router.post("/add-good")
def add_good(
        user_data: GoodCreateStrict | None = Body(None),
        db: Session = Depends(create_session)
):
    if user_data is None:
        raise HTTPException(status_code=400, detail="Payload لازم است")
    now = datetime.now(timezone.utc)
    good = Good(
        TypeGood=user_data.TypeGood,
        NumberGood=user_data.NumberGood,
        GivenToWhome=None,  # Must be set by another endpoint context if required
        GivenBy=user_data.GivenBy,
        UpdatedDate=now
    )
    db.add(good)
    db.commit()
    db.refresh(good)
    return good

def send_sms_service(phone_number, sms_code):
    username = " "  # نام کاربری اسان‌پیک
    password = " "  # رمز عبور اسان‌پیک
    sender_number = 3000  # شماره سرویس‌دهنده

    message = sms_code
    # URL API اسان‌پیک
    url = "https://panel.asanak.com/webservice/v1rest/sendsms"
    # داده‌های درخواست
    data = {
        'username': username,
        'password': password,
        'source': sender_number,
        'destination': phone_number,
        'message': message
    }
    try:
        # ارسال درخواست POST
        response = requests.post(url, data=data, timeout=30)

        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()

            # بررسی موفقیت‌آمیز بودن ارسال
            if result.get('status') == 'ok':
                return {
                    'success': True,
                    'message': 'پیامک با موفقیت ارسال شد',
                    'message_id': result.get('messageid'),
                    'status': result.get('status')
                }
            else:
                return {
                    'success': False,
                    'message': 'خطا در ارسال پیامک',
                    'error': result.get('message', 'خطای ناشناخته'),
                    'status': result.get('status')
                }
        else:
            return {
                'success': False,
                'message': 'خطا در ارتباط با سرور',
                'status_code': response.status_code,
                'error': response.text
            }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'اتصال به سرور زمان‌بر شد',
            'error': 'timeout'
        }

    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'خطا در اتصال به اینترنت',
            'error': 'connection_error'
        }

    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': 'خطا در ارسال درخواست',
            'error': str(e)
        }

    except Exception as e:
        return {
            'success': False,
            'message': 'خطای ناشناخته',
            'error': str(e)
        }

@router.post("/send-sms/{phone_number}/{good_id}")
def send_sms(
        good_id: int,
        phone_number: str,
        db: Session = Depends(create_session),
):
    sms_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    # send_sms_service(phone_number, {sms_code})

    good = db.query(Good).filter(Good.GoodID == good_id).first()
    if good:
        good.SmsCode = sms_code
        db.add(good)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="کمک پیدا نشد")
    return {"success": True, "message": "پیامک ارسال شد"}

@router.post("/verify-sms/{sms_code}/{good_id}")
def verify_sms(
        good_id: int,
        sms_code: str,
        db: Session = Depends(create_session)
):
    good = db.query(Good). filter(Good.GoodID == good_id).first()
    if good is None:
        raise HTTPException(status_code=404, detail="کالا پیدا نشد")
    if good.SmsCode == sms_code:
        good.Verified = True
        db.add(good)
        db.commit()
        return {"success": True, "message": " کد تایید شد"}
    else:
        return {"success": False, "message": "کد نامعتبر است"}
