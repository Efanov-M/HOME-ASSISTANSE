from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import DATABASE_URL


# engine как "технический вход" в PostgreSQL:
# он умеет открывать реальные подключения, но это ещё не тот объект,
# через который обычно создают, читают и обновляют ORM-сущности.
engine = create_engine(DATABASE_URL)

# SessionLocal - это фабрика, а не готовая сессия. Каждый вызов SessionLocal() создаёт отдельный объект Session,
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

def get_db():
    """This function:
    1. creates a new SQLAlchemy Session,
    2. yields it to the caller (e.g. FastAPI dependency),
    3. guarantees that the session is closed after use.

    RU: Предоставляет сессию базы данных на время выполнения запроса.

    Функция:
    1. создаёт новую Session,
    2. отдаёт её наружу (например, в endpoint или сервис),
    3. гарантированно закрывает соединение после завершения работы.
    """

    # 1. создаём новую сессию через фабрику SessionLocal
    # каждая сессия — это отдельное подключение/контекст работы с БД
    db = SessionLocal()

    try:
        # 2. отдаём сессию наружу здесь выполнение "приостанавливается", и код, который вызвал get_db(),
        # получает доступ к db (Session)
        yield db

    finally:
        # 3. этот блок выполнится ВСЕГДА даже если внутри запроса произошла ошибка
        # закрываем соединение с БД, чтобы не было утечек
        db.close()
