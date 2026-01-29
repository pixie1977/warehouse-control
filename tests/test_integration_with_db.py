import sys
from pathlib import Path
import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta

from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.booking.infrastructure.repositories import SqlAlchemyReservationRepository

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.booking.entrypoints.fastapi_app import app, get_uow
from src.booking.infrastructure.db_models import Base, ReservationModel
from src.booking.infrastructure.uow import SqlAlchemyUnitOfWork


TEST_DB_URL = "sqlite:///./test_reservations.db"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
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
def uow(test_engine):
    def session_factory():
        TestingSessionLocal = sessionmaker(bind=test_engine)
        return TestingSessionLocal()

    class FakeUoW:
        def __init__(self):
            self.session = session_factory()
            self.reservations = SqlAlchemyReservationRepository(self.session)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.session.close()

        def commit(self):
            self.session.commit()

        def rollback(self):
            self.session.rollback()

    return FakeUoW()


@pytest_asyncio.fixture
async def client(uow):
    def override_get_uow():
        return uow

    app.dependency_overrides[get_uow] = override_get_uow
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_reservation_persists_in_db(client, test_session):
    dto = {
        "slot_start": (datetime.now() + timedelta(hours=1)).isoformat(),
        "duration_min": 60,
        "party_size": 2
    }

    response = await client.post("/reservations", json=dto)
    assert response.status_code == 200
    data = response.json()
    reservation_id = data["reservation_id"]
    assert isinstance(reservation_id, str)

    saved = test_session.query(ReservationModel).filter_by(reservation_id=reservation_id).first()
    assert saved is not None
    assert saved.party_size == 2
    assert saved.status == "CREATED"
    assert saved.table_id is not None