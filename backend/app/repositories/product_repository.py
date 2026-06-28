from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from ..models.product import Product
from ..schemas.product import ProductCreate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def _filtered_query(self, search: Optional[str] = None):
        query = self.db.query(Product)
        if search:
            like = f"%{search}%"
            # ilike is Unicode case-insensitive on PostgreSQL (production).
            # On SQLite (local/dev) LIKE folds case for ASCII only, so a
            # lowercase Cyrillic query won't match a capitalised name there;
            # the storefront filters client-side, which handles this.
            query = query.filter(
                or_(
                    Product.name.ilike(like),
                    Product.brand.ilike(like),
                    Product.sku.ilike(like),
                )
            )
        return query

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[Product]:
        query = (
            self._filtered_query(search)
            .options(joinedload(Product.category))
            .order_by(Product.id)
        )
        if offset:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def count(self, search: Optional[str] = None) -> int:
        return self._filtered_query(search).count()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_category(self, category_id: int) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.category_id == category_id)
            .all()
        )

    def create(self, product_data: ProductCreate) -> Product:
        db_product = Product(**product_data.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_multiple_by_ids(self, product_ids: List[int]) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id.in_(product_ids))
            .all()
        )

    def update(self, product: Product, fields: dict) -> Product:
        for key, value in fields.items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()