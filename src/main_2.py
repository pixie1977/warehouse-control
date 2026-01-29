from datetime import datetime, timedelta

from booking.domain.model import TimeSlot, Reservation, TableId, PartySize
from booking.infrastructure.repositories import SqlAlchemyReservationRepository
from booking.infrastructure.database import SessionLocal


def main():
    # Создаём сессию
    session = SessionLocal()

    # Инициализируем репозиторий
    repo = SqlAlchemyReservationRepository(session)

    # Создаём таблицу (если ещё не создана)
    repo.create_all_tables()

    # Пример: добавление бронирования
    slot = TimeSlot(start=datetime.now(), end=datetime.now() + timedelta(hours=1))
    table_id = TableId("t1")
    party_size = PartySize(2)
    reservation = Reservation(table_id=table_id, slot=slot, party_size=party_size)

    repo.add(reservation)
    session.commit()

    # Получение
    saved = repo.get("r1")
    print(f"Saved: {saved}")

    session.close()

if __name__ == "__main__":
    main()