import pytest
from httpx import AsyncClient

# Импортируем app после настройки пути
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.booking.entrypoints.fastapi_app import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(base_url="http://test") as ac:
        yield ac