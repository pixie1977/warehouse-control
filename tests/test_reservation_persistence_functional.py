import sys
from pathlib import Path
import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta

from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.booking.entrypoints.fastapi_app import app, get_uow
from src.booking.infrastructure.db_models import Base, ReservationModel
from src.booking.infrastructure.uow import SqlAlchemyUnitOfWork


# Тестовая БД
TEST_DB_URL = "sqlite:///./test_reservations.db"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
    # Удаляем файл после всех тестов
    if os.path.exists("./test_reservations.db"):
        os.remove("./test_reservations.db")


@pytest.fixture
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False)
    session = TestingSessionLocal()
    yield session
    if session.is_active:
        session.rollback()
    session.close()


@pytest.fixture
def uow(test_session):
    """Фикстура UoW с реальной сессией"""
    return SqlAlchemyUnitOfWork(session=test_session)


@pytest_asyncio.fixture
async def client(uow):
    """Клиент с подменённым UoW"""
    def override_get_uow():
        return uow

    app.dependency_overrides[get_uow] = override_get_uow
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_reservation_is_saved_to_db(client, test_session):
    """
    Проверяем, что бронирование:
    1. Создаётся через API
    2. Возвращается с reservation_id
    3. Сохраняется в БД
    """
    dto = {
        "slot_start": (datetime.now() + timedelta(hours=1)).isoformat(),
        "duration_min": 60,
        "party_size": 2
    }

    response = await client.post("/reservations", json=dto)

    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    reservation_id = data["reservation_id"]
    assert isinstance(reservation_id, str)
    assert len(reservation_id) > 0

    # Проверяем, что запись есть в БД
    saved_model = test_session.query(ReservationModel).filter_by(reservation_id=reservation_id).first()
    assert saved_model is not None
    assert saved_model.party_size == 2
    assert saved_model.status == "CREATED"  # потому что handler вызывает confirm()
    assert saved_model.table_id == "T1"
    assert saved_model.start_time is not None
    assert saved_model.end_time is not None