from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from ..models.order import Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Order]:
        query = (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .order_by(Order.id.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.id == order_id)
            .first()
        )

    def count(self) -> int:
        return self.db.query(Order).count()
