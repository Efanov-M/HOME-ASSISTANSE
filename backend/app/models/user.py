from datetime import datetime
import enum

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(enum.Enum):
    """EN: Enumeration of user roles inside one family space.

    Using an enum makes the allowed role values explicit and easier to control.

    RU: Перечисление ролей пользователя внутри одной семейной группы.

    Использование enum делает допустимые значения роли явными
    и помогает лучше контролировать их в коде и схеме БД.
    """

    admin = "admin"
    user = "user"


class User(Base):
    """EN: ORM model for the ``users`` table.

    The class stores the core identity data for a user:
    email, password hash, role, activity flag, and relation to a family.

    RU: ORM-модель таблицы ``users``.

    Этот класс хранит базовые данные пользователя:
    email, хеш пароля, роль, признак активности и связь с семьёй.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    # Это очень полезный учебный приём:
    # вместо того чтобы везде доверять "обычным строкам", мы заворачиваем роль в Enum.
    # Так сама модель подсказывает, какие значения вообще допустимы.
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    # Обрати внимание на отличие от ``server_default``:
    # ``default=True`` срабатывает на стороне Python/ORM в момент создания объекта.
    # То есть значение появляется ещё до того, как INSERT уйдёт в базу.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    family_id: Mapped[int] = mapped_column(
        BigInteger,
        # ``ondelete="CASCADE"`` - это не "магия Python".
        # Это подсказка самой базе данных, что делать с зависимыми строками,
        # если родительская запись family будет удалена.
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    # Сейчас ``updated_at`` ведёт себя скорее как "поле с первоначальным временем":
    # значение проставляется при INSERT, но автоматическое обновление при UPDATE
    # ещё не настроено. Для раннего учебного этапа это обычное упрощение.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
