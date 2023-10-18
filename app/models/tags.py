from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin


class TagBase(CoreModel):
    label: Annotated[
        str, Field(..., json_schema_extra={'example': 'High Protein'})
    ]
    desc: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'At least 30% of the calories are protein.'
        })
    ]


class TagInDB(IDModelMixin, TagBase):
    pass


class TagOut(IDModelMixin, TagBase):
    pass


class TagsOut(CoreModel):
    tags: list[TagOut]
