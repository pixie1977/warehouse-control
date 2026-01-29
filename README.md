# Restaurant Booking (DDD + Clean Architecture)

Это учебный проект (bounded context **Booking**) для объяснения DDD и Clean Architecture на Python.

## Структура
- `src/booking/domain` — доменная модель (Entity/VO/Aggregate Root), инварианты, события, доменные сервисы, порты (Repository).
- `src/booking/application` — use-cases (handlers), Unit of Work порт.
- `src/booking/infrastructure` — адаптеры (in-memory repo/uow), заготовки под SQLAlchemy.
- `src/booking/entrypoints` — пример HTTP entrypoint (FastAPI-скелет без зависимости в pyproject).

## Быстрый старт (тесты)
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Доменные термины (Ubiquitous Language)
- Reservation — бронь
- TimeSlot — временной слот (start/end)
- PartySize — количество гостей
- TableId — идентификатор стола
- ReservationStatus — статус брони


Пример POST-запроса:

Формат времени: ISO 8601 (YYYY-MM-DDTHH:MM:SS)

curl -X POST "http://localhost:8000/reservations" \
     -H "Content-Type: application/json" \
     -d '{
           "slot_start": "2026-01-30T14:00:00",
           "duration_min": 60,
           "party_size": 3
         }'


Python: вызов через requests

import requests
import datetime
import json

url = "http://localhost:8000/reservations"

dto = {
    "slot_start": (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat(),
    "duration_min": 90,
    "party_size": 4
}

response = requests.post(url, json=dto)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Бронирование создано: {data['reservation_id']}")
else:
    print(f"❌ Ошибка: {response.status_code} — {response.text}")