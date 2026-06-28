from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from ..security import require_admin
from ..services.product_service import ProductService

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_products(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    search: Optional[str] = Query(
        None, description="Search by product name, brand or SKU"
    ),
):
    service = ProductService(db)
    return service.get_all_products(limit=limit, offset=offset, search=search)

@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product_by_id(product_id)

@router.get(
    "/category/{category_id}",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
)
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_products_by_category(category_id)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = ProductService(db)
    return service.create_product(product)

@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = ProductService(db)
    return service.update_product(product_id, product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = ProductService(db)
    service.delete_product(product_id)