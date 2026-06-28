from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .category import CategoryResponse


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200,
                            description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0,
                            description="Product price(must be greater than 0")
    category_id: int = Field(..., description='Category ID')
    image_url: Optional[str] = Field(None, description='Product image URL')
    stock: int = Field(0, ge=0, description='Available stock')
    brand: Optional[str] = Field(None, description='Brand name')
    sku: Optional[str] = Field(None, description='Article number')
    unit: str = Field("шт", description='Unit: шт / упаковка')
    pack_qty: int = Field(1, ge=1, description='Quantity per pack')

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    brand: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    pack_qty: Optional[int] = Field(None, ge=1)

class ProductResponse(BaseModel):
    id: int = Field(..., description="Unique product ID")
    name: str
    description: Optional[str]
    price: float
    category_id: int
    image_url: Optional[str]
    stock: int
    brand: Optional[str]
    sku: Optional[str]
    unit: str
    pack_qty: int
    created_at: datetime
    category: CategoryResponse = Field(..., description="Product category details")

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int = Field(..., description='Total number of products')