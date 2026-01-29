import uuid
from datetime import timedelta

from .model import Reservation, TimeSlot, PartySize, TableId, ReservationStatus


class ReservationFactory:
    @staticmethod
    def create(slot_start, duration_min, party_size):
        return Reservation(
            reservation_id=str(uuid.uuid4()),  # ← генерируем id
            slot=TimeSlot(start=slot_start, end=slot_start + timedelta(minutes=duration_min)),
            party_size=PartySize(value=party_size),
            status=ReservationStatus.CREATED,
            table_id=None,
        )