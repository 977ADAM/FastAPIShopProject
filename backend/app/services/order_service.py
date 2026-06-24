import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.order import Order, OrderItem
from ..repositories.order_repository import OrderRepository
from ..repositories.product_repository import ProductRepository
from ..schemas.order import OrderCreate, OrderListResponse, OrderResponse

logger = logging.getLogger("app.orders")

VALID_STATUSES = {"pending", "paid", "shipped", "completed", "cancelled"}


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repository = OrderRepository(db)
        self.product_repository = ProductRepository(db)

    def create_order(self, data: OrderCreate) -> OrderResponse:
        # Aggregate quantities per product (guards against duplicate lines).
        quantities: dict[int, int] = {}
        for item in data.items:
            quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity

        products = self.product_repository.get_multiple_by_ids(list(quantities))
        products_by_id = {p.id: p for p in products}

        total = 0.0
        order_items: list[OrderItem] = []
        for product_id, quantity in quantities.items():
            product = products_by_id.get(product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with id {product_id} does not exist",
                )
            if product.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Not enough stock for '{product.name}' "
                    f"(requested {quantity}, available {product.stock})",
                )
            subtotal = product.price * quantity
            total += subtotal
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    quantity=quantity,
                )
            )
            product.stock -= quantity

        order = Order(
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            total=round(total, 2),
            status="pending",
            items=order_items,
        )
        order = self.order_repository.create(order)
        self._notify_order_created(order)
        return OrderResponse.model_validate(order)

    def get_all_orders(self, limit=None, offset: int = 0) -> OrderListResponse:
        orders = self.order_repository.get_all(limit=limit, offset=offset)
        return OrderListResponse(
            orders=[OrderResponse.model_validate(o) for o in orders],
            total=self.order_repository.count(),
        )

    def get_order_by_id(self, order_id: int) -> OrderResponse:
        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found",
            )
        return OrderResponse.model_validate(order)

    def update_status(self, order_id: int, new_status: str) -> OrderResponse:
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Allowed: {sorted(VALID_STATUSES)}",
            )
        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found",
            )
        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        return OrderResponse.model_validate(order)

    def _notify_order_created(self, order: Order) -> None:
        """Order-confirmation hook.

        Durable, infra-free stand-in for sending a confirmation email: logs a
        structured line. Swap this for an SMTP/provider call when email is wired up.
        """
        logger.info(
            "ORDER CONFIRMATION order_id=%s email=%s total=%.2f items=%d",
            order.id,
            order.customer_email,
            order.total,
            len(order.items),
        )
