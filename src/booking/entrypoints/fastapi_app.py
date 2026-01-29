from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime

from src.booking.application.commands import CreateReservation
from src.booking.application.handlers import CreateReservationHandler
from src.booking.domain.services import TableAllocationService
from src.booking.infrastructure.available_tables import get_available_tables


# Глобальная зависимость
def get_uow():
    from src.booking.infrastructure.uow import InMemoryUnitOfWork
    return InMemoryUnitOfWork()


app = FastAPI()

class CreateReservationDTO(BaseModel):
    slot_start: datetime
    duration_min: int
    party_size: int


@app.post("/reservations")
def create_reservation(dto: CreateReservationDTO, uow=Depends(get_uow)):
    service = TableAllocationService()
    handler = CreateReservationHandler(uow=uow, allocator=service)
    cmd = CreateReservation(**dto.dict())
    reservation_id = handler(cmd, available_tables=get_available_tables())
    return {"reservation_id": reservation_id}