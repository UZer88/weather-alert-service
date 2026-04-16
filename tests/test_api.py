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


# ========== Тесты для подписок ==========

@pytest.mark.anyio
async def test_create_subscription(client):
    # Регистрация и логин
    await client.post("/auth/register", json={
        "email": "subuser@example.com",
        "password": "subpass"
    })
    login_resp = await client.post(
        "/auth/login",
        data={"username": "subuser@example.com", "password": "subpass"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создание подписки
    response = await client.post(
        "/subscriptions/",
        json={"city": "Moscow"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Moscow"
    assert "id" in data


@pytest.mark.anyio
async def test_create_duplicate_subscription(client):
    # Регистрация и логин
    await client.post("/auth/register", json={
        "email": "dupsub@example.com",
        "password": "duppass"
    })
    login_resp = await client.post(
        "/auth/login",
        data={"username": "dupsub@example.com", "password": "duppass"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Первое создание
    await client.post("/subscriptions/", json={"city": "Moscow"}, headers=headers)
    # Второе создание (дубликат)
    response = await client.post("/subscriptions/", json={"city": "Moscow"}, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.text.lower()


@pytest.mark.anyio
async def test_get_subscriptions(client):
    # Регистрация и логин
    await client.post("/auth/register", json={
        "email": "getsub@example.com",
        "password": "getpass"
    })
    login_resp = await client.post(
        "/auth/login",
        data={"username": "getsub@example.com", "password": "getpass"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём подписку
    await client.post("/subscriptions/", json={"city": "London"}, headers=headers)

    # Получаем список подписок
    response = await client.get("/subscriptions/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["city"] == "London"


@pytest.mark.anyio
async def test_delete_subscription(client):
    # Регистрация и логин
    await client.post("/auth/register", json={
        "email": "delsub@example.com",
        "password": "delpass"
    })
    login_resp = await client.post(
        "/auth/login",
        data={"username": "delsub@example.com", "password": "delpass"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём подписку
    create_resp = await client.post("/subscriptions/", json={"city": "Berlin"}, headers=headers)
    sub_id = create_resp.json()["id"]

    # Удаляем подписку
    delete_resp = await client.delete(f"/subscriptions/{sub_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Subscription deleted"

    # Проверяем, что подписка действительно удалена (получаем список — её нет)
    get_resp = await client.get("/subscriptions/", headers=headers)
    assert len(get_resp.json()) == 0


@pytest.mark.anyio
async def test_delete_nonexistent_subscription(client):
    # Регистрация и логин
    await client.post("/auth/register", json={
        "email": "del404@example.com",
        "password": "del404"
    })
    login_resp = await client.post(
        "/auth/login",
        data={"username": "del404@example.com", "password": "del404"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Пытаемся удалить несуществующую подписку
    response = await client.delete("/subscriptions/99999", headers=headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_subscription_unauthorized(client):
    # Попытка создать подписку без токена
    response = await client.post(
        "/subscriptions/",
        json={"city": "Moscow"}
    )
    assert response.status_code == 401