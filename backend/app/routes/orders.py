from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.order import (
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from ..security import require_admin
from ..services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return OrderService(db).create_order(order)


@router.get("", response_model=OrderListResponse, status_code=status.HTTP_200_OK)
def list_orders(
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return OrderService(db).get_all_orders(limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    return OrderService(db).get_order_by_id(order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    return OrderService(db).update_status(order_id, payload.status)
