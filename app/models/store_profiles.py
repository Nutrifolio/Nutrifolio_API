from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin


class StoreProfileBase(CoreModel):
    name: Annotated[
        str, Field(..., json_schema_extra={'example': 'Starbucks'})
    ]
    logo_url: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'https://domain.com/path/logo.png'
        })
    ]
    description: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'More than just great coffee.'
        })
    ]
    phone_number: Annotated[
        Optional[int], 
        Field(default=None, json_schema_extra={'example': 6940946282})
    ]
    address: Annotated[
        str, 
        Field(..., json_schema_extra={
            'example': 'Agiou Ioannou, Agia Paraskevi 153 42'
        })
    ]
    lat: Annotated[float, Field(..., json_schema_extra={'example': 38.011726})]
    lng: Annotated[float, Field(..., json_schema_extra={'example': 23.822457})]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class StoreProfileCreate(StoreProfileBase):
    pass


class StoreProfileInDB(IDModelMixin, StoreProfileBase):
    pass


class StoreProfileOut(IDModelMixin, StoreProfileBase):
    pass


class StoreProfileOutProductDetailed(IDModelMixin):
    # The id contained in this model will actually be the store_id
    name: Annotated[
        str, Field(..., json_schema_extra={'example': 'Starbucks'})
    ]
    logo_url: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'https://domain.com/path/logo.png'
        })
    ]
    address: Annotated[
        str, 
        Field(..., json_schema_extra={
            'example': 'Agiou Ioannou, Agia Paraskevi 153 42'
        })
    ]
    lat: Annotated[float, Field(..., json_schema_extra={'example': 38.011726})]
    lng: Annotated[float, Field(..., json_schema_extra={'example': 23.822457})]


class StoreProfileOutFilter(IDModelMixin):
    # The id contained in this model will actually be the store_id
    name: Annotated[
        str, Field(..., json_schema_extra={'example': 'Starbucks'})
    ]
    logo_url: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'https://domain.com/path/logo.png'
        })
    ]
    distance_km: Annotated[
        float, Field(..., json_schema_extra={'example': 1.23})
    ]
