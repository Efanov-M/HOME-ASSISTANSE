from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Это временное упрощение для учебного этапа.
# Пока строка подключения лежит прямо здесь, чтобы вся базовая настройка БД
# была видна в одном месте и не расползалась по нескольким файлам слишком рано.
DATABASE_URL = "postgresql+psycopg://home_secretary:YOUR_PASSWORD@localhost:5432/home_secretary"


# Представь engine как "технический вход" в PostgreSQL:
# он умеет открывать реальные подключения, но это ещё не тот объект,
# через который обычно создают, читают и обновляют ORM-сущности.
engine = create_engine(DATABASE_URL)

# SessionLocal - это фабрика, а не готовая сессия.
# Каждый вызов SessionLocal() создаёт отдельный объект Session,
# и уже эта Session становится рабочим столом для ORM-операций.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# Base - это общий родитель для ORM-моделей.
# Как только класс наследуется от Base, SQLAlchemy начинает воспринимать его
# как часть declarative-подхода и ждёт, что внутри будет описание таблицы.
Base = declarative_base()
