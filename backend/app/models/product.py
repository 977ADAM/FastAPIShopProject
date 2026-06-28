from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .category import Category


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    brand: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    unit: Mapped[str] = mapped_column(
        String, nullable=False, default="шт", server_default="шт"
    )
    pack_qty: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    category: Mapped["Category"] = relationship(back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
