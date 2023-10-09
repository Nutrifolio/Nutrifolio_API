from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin


class StoreProfileBase(CoreModel):
    name: Annotated[str, Field(..., json_schema_extra={
        'example': 'Starbucks'
    })]
    logo_url: Annotated[Optional[str], Field(default=None, json_schema_extra={
        'example': 'https://domain.com/path/logo.png'
    })]
    lat: Annotated[float, Field(..., json_schema_extra={'example': 38.011726})]
    lng: Annotated[float, Field(..., json_schema_extra={'example': 23.822457})]


class StoreProfileCreate(StoreProfileBase):
    phone_number: Annotated[
        Optional[int], 
        Field(default=None, json_schema_extra={'example': 6940946282})
    ]
    address: Annotated[str, Field(..., json_schema_extra={
        'example': 'Agiou Ioannou, Agia Paraskevi 153 42'
    })]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class StoreProfileInDB(IDModelMixin, StoreProfileBase):
    phone_number: Annotated[
        Optional[int], 
        Field(default=None, json_schema_extra={'example': 6940946282})
    ]
    address: Annotated[str, Field(..., json_schema_extra={
        'example': 'Agiou Ioannou, Agia Paraskevi 153 42'
    })]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class StoreProfileOut(IDModelMixin, StoreProfileBase):
    phone_number: Annotated[
        Optional[int], 
        Field(default=None, json_schema_extra={'example': 6940946282})
    ]
    address: Annotated[str, Field(..., json_schema_extra={
        'example': 'Agiou Ioannou, Agia Paraskevi 153 42'
    })]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]
