from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """EN: ORM model for the ``audit_logs`` table.

    Audit logs are useful because they preserve a history of security-related
    actions even when the main business objects later change or disappear.

    RU: ORM-модель таблицы ``audit_logs``.

    Журнал аудита полезен тем, что сохраняет историю событий безопасности,
    даже если основные бизнес-объекты позже изменятся или будут удалены.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        # Это осознанно "бережный" вариант:
        # если пользователь исчезнет, след аудита всё равно должен выжить.
        # Поэтому запись журнала остаётся, а прямой идентификатор просто станет NULL.
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(Text, nullable=False)

    ip_address: Mapped[str | None] = mapped_column(INET)

    user_agent: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ``details`` - это место, где журнал может хранить дополнительный контекст,
    # не заставляя нас создавать отдельную SQL-колонку под каждую мелочь.
    # Для такой гибкой метаинформации JSONB очень удобен.
    details: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
