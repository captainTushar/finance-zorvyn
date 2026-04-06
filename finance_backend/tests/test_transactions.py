from collections.abc import AsyncGenerator

from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app as fastapi_app
from app.models.user import User, UserRole
from app.services.auth_service import hash_password


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    test_db_url = "sqlite:///./test_transactions.db"
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
    db.add_all(
        [
            User(
                name="Admin",
                email="admin@test.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.admin,
                is_active=True,
            ),
            User(
                name="Analyst",
                email="analyst@test.com",
                hashed_password=hash_password("analyst123"),
                role=UserRole.analyst,
                is_active=True,
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
async def test_admin_create_then_analyst_fetch_transaction(client: AsyncClient) -> None:
    admin_token = await get_token(client, "admin@test.com", "admin123")
    analyst_token = await get_token(client, "analyst@test.com", "analyst123")

    create_response = await client.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "amount": 350.0,
            "type": "income",
            "category": "freelance",
            "date": str(date.today()),
            "notes": "project payment",
        },
    )
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]

    get_response = await client.get(
        f"/api/transactions/{transaction_id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["category"] == "freelance"


@pytest.mark.asyncio
async def test_soft_deleted_transaction_not_listed(client: AsyncClient) -> None:
    admin_token = await get_token(client, "admin@test.com", "admin123")

    create_response = await client.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "amount": 99.0,
            "type": "expense",
            "category": "transport",
            "date": str(date.today()),
            "notes": "cab",
        },
    )
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/transactions/{transaction_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_response.status_code == 204

    list_response = await client.get(
        "/api/transactions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_response.status_code == 200
    ids = [item["id"] for item in list_response.json()]
    assert transaction_id not in ids
