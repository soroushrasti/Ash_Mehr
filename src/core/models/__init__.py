from typing import Optional, Type
from pydantic import create_model
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def sqlalchemy_model_to_pydantic(model: Type[DeclarativeMeta], exclude: Optional[list] = None):
    exclude = exclude or []
    fields = {}
    for column in model.__table__.columns:
        if column.name in exclude:
            continue
        try:
            python_type = column.type.python_type
        except (NotImplementedError, AttributeError):
            python_type = str
        default = ... if not column.nullable and not column.default else None
        fields[column.name] = (python_type, default)
    return create_model(f"{model.__name__}Create", **fields)
