from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from ..security import require_admin
from ..services.category_service import CategoryService

router = APIRouter(
    prefix="/api/categories",
    tags=['categories']
)

@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.get_all_categories()

@router.get('/{category_id}', response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def get_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.get_category_by_id(category_id)

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = CategoryService(db)
    return service.create_category(category)

@router.put('/{category_id}', response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = CategoryService(db)
    return service.update_category(category_id, category)

@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = CategoryService(db)
    service.delete_category(category_id)