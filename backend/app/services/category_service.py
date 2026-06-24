from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories.category_repository import CategoryRepository
from ..schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def get_all_categories(self) -> List[CategoryResponse]:
        categories = self.repository.get_all()
        return [CategoryResponse.model_validate(cat) for cat in categories]

    def get_category_by_id(self, category_id: int) -> CategoryResponse:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with id {category_id} not found'
            )
        return CategoryResponse.model_validate(category)

    def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        existing = self.repository.get_by_slug(category_data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with slug '{category_data.slug}' already exists"
            )
        category = self.repository.create(category_data)
        return CategoryResponse.model_validate(category)

    def update_category(self, category_id: int, category_data: CategoryUpdate) -> CategoryResponse:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with id {category_id} not found'
            )
        fields = category_data.model_dump(exclude_unset=True)
        category = self.repository.update(category, fields)
        return CategoryResponse.model_validate(category)

    def delete_category(self, category_id: int) -> None:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with id {category_id} not found'
            )
        if category.products:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a category that still has products"
            )
        self.repository.delete(category)