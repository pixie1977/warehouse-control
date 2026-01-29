from __future__ import annotations

from typing import Mapping, Iterable

from .commands import CreateReservation
from ..application.unit_of_work import UnitOfWork
from ..domain.factory import ReservationFactory
from ..domain.model import ReservationAggregate
from ..domain.services import TableAllocationService


class CreateReservationHandler:
    """
    Use Case (Application Service):

    - создает агрегат (Factory)
    - вызывает доменные правила (Domain Service + методы Aggregate Root)
    - сохраняет через UoW/Repository
    """

    def __init__(self, uow: UnitOfWork, allocator: TableAllocationService):
        self.uow = uow
        self.allocator = allocator

    def __call__(self, cmd: CreateReservation, available_tables: Iterable[Mapping]) -> str:
        reservation = ReservationFactory.create(
            slot_start=cmd.slot_start,
            duration_min=cmd.duration_min,
            party_size=cmd.party_size,
        )

        reservation_aggregate = ReservationAggregate(root=reservation)

        table_id = self.allocator.allocate(reservation, available_tables)
        reservation_aggregate.assign_table(table_id)

        with self.uow:
            self.uow.reservations.add(reservation)
            self.uow.commit()

        return reservation.reservation_id
