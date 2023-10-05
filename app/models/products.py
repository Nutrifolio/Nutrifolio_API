from typing import Optional
from app.models.core import CoreModel, IDModelMixin


class ProductBase(CoreModel):
    """
    All common characteristics of our Product resource
    """
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ProductCreate(ProductBase):
    name: str
    price: float


class ProductUpdate(ProductBase):
    pass


class ProductInDB(IDModelMixin, ProductBase):
    name: str
    price: float


class ProductPublic(IDModelMixin, ProductBase):
    pass
