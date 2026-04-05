from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RefreshToken(Base):
    """EN: ORM model for the ``refresh_tokens`` table.

    It keeps long-lived refresh token records that can later be revoked,
    checked for expiration, and linked back to a specific user.

    RU: ORM-модель таблицы ``refresh_tokens``.

    Она хранит записи о долгоживущих refresh token,
    которые потом можно отзывать, проверять на истечение
    и связывать с конкретным пользователем.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    
    # если по дизайну в БД должен жить только hash, то сам "сырой" refresh token
    # лучше вообще не хранить в таблице.
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # В PostgreSQL есть специальный тип ``INET`` для IP-адресов.
    # Он выразительнее, чем просто хранить адрес как обычный текст.
    ip_address: Mapped[str | None] = mapped_column(INET)

    user_agent: Mapped[str | None] = mapped_column(Text)
