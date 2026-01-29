from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from .db_models import ReservationModel, Base
from ..domain.model import Reservation, TimeSlot
from ..domain.repository import ReservationRepository


class InMemoryReservationRepository(ReservationRepository):
    def __init__(self) -> None:
        self._items: dict[str, Reservation] = {}

    def get(self, reservation_id: str) -> Optional[Reservation]:
        return self._items.get(reservation_id)

    def add(self, reservation: Reservation) -> None:
        self._items[reservation.reservation_id] = reservation

    def list_for_slot(self, slot: TimeSlot) -> List[Reservation]:
        return [r for r in self._items.values() if r.slot == slot]


class SqlAlchemyReservationRepository(ReservationRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, reservation_id: str) -> Optional[Reservation]:
        model = self.session.query(ReservationModel).filter_by(reservation_id=reservation_id).first()
        if model:
            return Reservation(
                reservation_id=model.reservation_id,
                table_id=model.table_id,
                status=model.status,
                slot=TimeSlot(start=model.start_time, end=model.end_time)
            )
        return None

    def add(self, reservation: Reservation) -> None:
        model = ReservationModel(
            reservation_id=reservation.reservation_id,
            table_id=reservation.table_id.value if reservation.table_id else None,
            status=reservation.status.value,
            start_time=reservation.slot.start,
            end_time=reservation.slot.end,
            party_size=reservation.party_size.value,
        )
        self.session.add(model)

    def list_for_slot(self, slot: TimeSlot) -> List[Reservation]:
        models = (self.session.query(ReservationModel)
                  .filter(ReservationModel.start_time == slot.start)
                  .filter(ReservationModel.end_time == slot.end)
                  .all())
        return [
            Reservation(
                reservation_id=m.reservation_id,
                table_id=m.table_id,
                status=m.status,
                slot=TimeSlot(start=m.start_time, end=m.end_time)
            ) for m in models
        ]

    def create_all_tables(self):
        """Создаёт таблицы (вызывать один раз при старте приложения)"""
        Base.metadata.create_all(bind=self.session.bind)