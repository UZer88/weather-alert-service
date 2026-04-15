import os
import pytest
from httpx import AsyncClient, ASGITransport

# Устанавливаем тестовую БД ДО импорта app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models import Base
from app.database import engine

# Фикстура для anyio, чтобы избежать ScopeMismatch
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# Создание и удаление таблиц БД
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Клиент для тестов
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# ========== Тесты ==========

@pytest.mark.anyio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.anyio
async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "pass123"
    })
    response = await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "pass456"
    })
    assert response.status_code == 400
    assert "already" in response.text.lower()

@pytest.mark.anyio
async def test_register_invalid_email(client):
    response = await client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "secret123"
    })
    assert response.status_code == 422

@pytest.mark.anyio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "secretpass"
    })
    response = await client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "secretpass"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.anyio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "wrongpass@example.com",
        "password": "correctpass"
    })
    response = await client.post(
        "/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.text.lower()

@pytest.mark.anyio
async def test_login_nonexistent_user(client):
    response = await client.post(
        "/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "anything"
        }
    )
    assert response.status_code == 401