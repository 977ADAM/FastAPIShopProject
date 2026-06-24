
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories.category_repository import CategoryRepository
from ..repositories.product_repository import ProductRepository
from ..schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)


class ProductService:
    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    def get_all_products(
        self,
        limit=None,
        offset: int = 0,
        search=None,
    ) -> ProductListResponse:
        products = self.product_repository.get_all(limit=limit, offset=offset, search=search)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        total = self.product_repository.count(search=search)
        return ProductListResponse(products=products_response, total=total)

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        return ProductResponse.model_validate(product)

    def get_products_by_category(self, category_id: int) -> ProductListResponse:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        products = self.product_repository.get_by_category(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        category = self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist"
            )

        product = self.product_repository.create(product_data)
        return ProductResponse.model_validate(product)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        fields = product_data.model_dump(exclude_unset=True)
        if "category_id" in fields:
            category = self.category_repository.get_by_id(fields["category_id"])
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with id {fields['category_id']} does not exist"
                )

        product = self.product_repository.update(product, fields)
        return ProductResponse.model_validate(product)

    def delete_product(self, product_id: int) -> None:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        self.product_repository.delete(product)