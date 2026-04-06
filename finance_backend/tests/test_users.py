from collections.abc import AsyncGenerator

from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app as fastapi_app
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.services.auth_service import hash_password


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    test_db_url = "sqlite:///./test_users.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db

    db: Session = TestingSessionLocal()
    viewer = User(
        name="Viewer",
        email="viewer@test.com",
        hashed_password=hash_password("viewer123"),
        role=UserRole.viewer,
        is_active=True,
    )
    admin = User(
        name="Admin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    db.add_all([viewer, admin])
    db.commit()
    db.refresh(admin)

    db.add_all(
        [
            Transaction(
                amount=1000.0,
                type=TransactionType.income,
                category="salary",
                date=date.today(),
                notes="salary",
                created_by=admin.id,
            ),
            Transaction(
                amount=250.0,
                type=TransactionType.expense,
                category="utilities",
                date=date.today(),
                notes="utilities",
                created_by=admin.id,
            ),
        ]
    )
    db.commit()
    db.close()

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


async def get_token(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_viewer_cannot_create_transaction(client: AsyncClient) -> None:
    token = await get_token(client, "viewer@test.com", "viewer123")
    response = await client.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": 100.0,
            "type": "expense",
            "category": "rent",
            "date": str(date.today()),
            "notes": "forbidden",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_dashboard_summary_totals(client: AsyncClient) -> None:
    token = await get_token(client, "admin@test.com", "admin123")
    response = await client.get(
        "/api/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_income"] == 1000.0
    assert body["total_expenses"] == 250.0
    assert body["net_balance"] == 750.0
    assert body["total_transactions"] == 2
