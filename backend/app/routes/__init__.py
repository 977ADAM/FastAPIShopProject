from .auth import router as auth_router
from .cart import router as cart_router
from .categories import router as categories_router
from .orders import router as orders_router
from .products import router as products_router
from .uploads import router as uploads_router

__all__ = [
    "products_router",
    "categories_router",
    "cart_router",
    "auth_router",
    "uploads_router",
    "orders_router",
]
