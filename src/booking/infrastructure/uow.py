from __future__ import annotations

from sqlalchemy.orm import Session

from ..application.unit_of_work import UnitOfWork
from ..infrastructure.repositories import InMemoryReservationRepository, SqlAlchemyReservationRepository


class InMemoryUnitOfWork(UnitOfWork):
    """UoW для тестов/демо без БД."""

    def __init__(self) -> None:
        self.reservations = InMemoryReservationRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


# Заготовка под SQLAlchemy UoW (для лекции / дальнейшего расширения)
class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session):  # ← Должен принимать session
        self.session = session
        self.reservations = SqlAlchemyReservationRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()