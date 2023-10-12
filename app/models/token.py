from typing import Annotated
from datetime import datetime, timedelta
from pydantic import Field
from app.models.core import CoreModel
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


class JWTPayloadUser(CoreModel):
    user_id: int
    iat: float
    exp: float


class JWTPayloadStore(CoreModel):
    store_id: int
    iat: float
    exp: float


class AccessToken(CoreModel):
    access_token: Annotated[
        str, 
        Field(..., json_schema_extra={
            'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJpYXQiOjE2OTY2NzE2NzYuNDY1MTQ3LCJleHAiOjE2OTcyNzY0NzYuNDY1MTU1fQ.4wH-Cnot-pwN1aZ87sTjZyQBe5oQOZ-RITjnsnA5T5I'
        })
    ]
    token_type: Annotated[
        str, Field(..., json_schema_extra={'example': 'bearer'})
    ]
