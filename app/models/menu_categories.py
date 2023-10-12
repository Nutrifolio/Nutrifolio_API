from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin


class MenuCategoryBase(CoreModel):
    label: Annotated[
        str, Field(..., json_schema_extra={'example': 'Salads'})
    ]
    desc: Annotated[
        Optional[str], 
        Field(default=None, json_schema_extra={
            'example': 'The Salads category offers a diverse selection of fresh and nutritious salads.'
        })
    ]


class MenuCategoryInDB(IDModelMixin, MenuCategoryBase):
    pass


class MenuCategoryOut(IDModelMixin, MenuCategoryBase):
    pass
