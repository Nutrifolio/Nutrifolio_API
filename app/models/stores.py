from typing import Annotated
from datetime import datetime
from pydantic import Field, EmailStr, field_validator
from email_validator import validate_email
from app.models.core import CoreModel, IDModelMixin


class StoreBase(CoreModel):
    """
    All common characteristics of our Store resource
    """
    email: Annotated[EmailStr, Field(..., json_schema_extra={
        'example': 'admin@mystore.com'
    })]


class StoreCreate(StoreBase):
    password: Annotated[str, Field(..., json_schema_extra={
        'example': 'mysecretpassword'
    })]
    conf_password: Annotated[str, Field(..., json_schema_extra={
        'example': 'mysecretpassword'
    })]

    @field_validator('email')
    def email_validation(cls, email):
        validate_email(email)
        return email

    @field_validator('password')
    def password_strength(cls, password):
        if len(password) < 12:
            raise ValueError(
                'Weak password: Should be at least 12 characters long.')
        return password

    @field_validator('conf_password')
    def passwords_match(cls, conf_password, values):
        if 'password' in values.data and conf_password != values.data["password"]:
            raise ValueError('Passwords do not match.')
        return conf_password


class StoreInDB(IDModelMixin, StoreBase):
    password: Annotated[str, Field(..., json_schema_extra={
        'example': 'mysecretpassword'
    })]
    is_verified: Annotated[bool, Field(..., json_schema_extra={
        'example': True
    })]


class StoreOut(IDModelMixin, StoreBase):
    pass
