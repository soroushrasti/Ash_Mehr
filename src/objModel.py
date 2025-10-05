# Rebuild RegisterCreateWithChildren using patched bases
from datetime import date
from typing import Optional

from pydantic import create_model

from src.core.models.good import GoodCreate
from src.core.models.register import RegisterCreateBase, ChildrenOfRegisterCreatePatched

RegisterCreateWithChildren = create_model(
    "RegisterCreateWithChildren",
    __base__=RegisterCreateBase,
    children_of_registre=(Optional[list[ChildrenOfRegisterCreatePatched]], None),
    goods_of_registre=(Optional[list[GoodCreate]], None),
    BirthDate=(Optional[date | str], None),
    UnderWhichAdmin=(Optional[int | str], None),
)