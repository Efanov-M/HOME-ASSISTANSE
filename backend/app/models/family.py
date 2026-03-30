from sqlalchemy import BigInteger, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.database import Base


class Family(Base):
    """EN: ORM model for the ``families`` table.

    This class describes how a family group is represented in Python code
    and how that representation maps to the database table.

    RU: ORM-модель таблицы ``families``.

    Этот класс показывает, как семейная группа выглядит в Python-коде
    и как это описание связывается с одноимённой таблицей в базе данных.
    """

    __tablename__ = "families"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # Важная учебная деталь: время тут заполняет не Python-код.
    # Его подставляет сама база данных, а это часто надёжнее и делает БД
    # единым источником правды для технических временных меток.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    # На этом этапе ``created_by`` хранится просто как числовое поле.
    # То есть мы уже сохраняем идею "кто создал семью",
    # но пока не заставляем SQLAlchemy оформлять это как внешний ключ.
    created_by: Mapped[int] = mapped_column(BigInteger)
