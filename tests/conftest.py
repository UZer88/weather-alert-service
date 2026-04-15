import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

# Импорты из вашего приложения
from app.main import app

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для тестирования API"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
