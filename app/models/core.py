from typing import Annotated
from pydantic import BaseModel, Field


class CoreModel(BaseModel):
    """
    Any common logic to be shared by all models goes here.
    """
    pass


class DetailResponse(BaseModel):
    detail: str


class IDModelMixin(BaseModel):
    id: Annotated[int, Field(..., json_schema_extra={'example': 1})]
