"""Pytest fixtures: isolated in-memory SQLite DB and a TestClient.

The app's get_db dependency is overridden with a session bound to an in-memory
engine, so tests never touch the real shop.db. TestClient is created without the
context-manager form on purpose, so the lifespan (which calls init_db on the
real database) does not run.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.category import Category
from app.models.product import Product


@pytest.fixture
def seeded_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    category = Category(name="Electronics", slug="electronics")
    session.add(category)
    session.commit()
    session.refresh(category)

    product = Product(
        name="Wireless Headphones",
        description="Noise cancelling",
        price=299.99,
        category_id=category.id,
        image_url="https://example.com/img.jpg",
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    try:
        yield {"session": session, "category": category, "product": product}
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(seeded_db):
    def override_get_db():
        yield seeded_db["session"]

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
