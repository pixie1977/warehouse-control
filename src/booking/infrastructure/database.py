from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

# TODO:: Движок БД (используем SQLite для простоты, в проме вынести в конфиг)
engine = create_engine("sqlite:///bookings.db", echo=True)

# Фабрика сессий
SessionLocal = sessionmaker(bind=engine)


# Зависимость для получения сессии (полезно при интеграции с FastAPI и т.п.)
def get_db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
