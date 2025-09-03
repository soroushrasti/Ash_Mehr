from typing import Optional, Type
from pydantic import create_model, BaseModel, ConfigDict
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import engine

Base = declarative_base()

# Base for Pydantic models enabling ORM instance serialization (Pydantic v2)
class _FromAttrsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

def _build_fields(model: Type[DeclarativeMeta], exclude: Optional[list] = None):
    exclude = exclude or []
    fields = {}
    for column in model.__table__.columns:
        if column.name in exclude:
            continue
        try:
            python_type = column.type.python_type
        except (NotImplementedError, AttributeError):
            python_type = str
        # Make every field optional for API schemas by default
        fields[column.name] = (Optional[python_type], None)  # type: ignore[arg-type]
    return fields


def sqlalchemy_model_to_pydantic(model: Type[DeclarativeMeta], exclude: Optional[list] = None):
    fields = _build_fields(model, exclude)
    return create_model(f"{model.__name__}Create", __base__=_FromAttrsBase, **fields)

# New: allow creating a Pydantic model with a custom name for response schemas

def sqlalchemy_model_to_pydantic_named(model: Type[DeclarativeMeta], name: str, exclude: Optional[list] = None):
    fields = _build_fields(model, exclude)
    return create_model(name, __base__=_FromAttrsBase, **fields)
