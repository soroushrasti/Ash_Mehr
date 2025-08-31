from fastapi import APIRouter, Depends

from ..config.authentication import authenticate

router = APIRouter(dependencies=[Depends(authenticate)])

from . import admin, register, good, message





