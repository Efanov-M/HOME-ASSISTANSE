from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """EN: Repository for working with ``audit_logs`` records.

    Audit repositories are often intentionally simple:
    write a log entry and later read log history back.

    RU: Репозиторий для работы с записями ``audit_logs``.

    Репозитории аудита часто специально делают простыми:
    записать событие в журнал и позже прочитать историю назад.
    """

    def __init__(self, db: Session):
        """EN: Accept the active session used for audit read/write operations.

        Args:
            db: Active SQLAlchemy session used to insert and read audit rows.

        RU: Принимает активную сессию для операций записи и чтения аудита.

        Аргументы:
            db: активная SQLAlchemy-сессия для добавления и чтения записей аудита.
        """

        self.db = db

    def create_audit_log(
        self,
        user_id: int | None,
        event_type: str,
        ip_address: str | None,
        user_agent: str | None,
        details: dict,
    ) -> AuditLog:
        """EN: Create a security audit entry and return the saved ORM object.

        Args:
            user_id: Related user identifier or ``None`` if the event is anonymous.
            event_type: Short event name, for example login or logout.
            ip_address: Client IP address if available.
            user_agent: Client user-agent string if available.
            details: Extra event metadata stored in JSONB.

        Returns:
            Saved ``AuditLog`` ORM object.

        RU: Создаёт запись аудита безопасности и возвращает сохранённый ORM-объект.

        Аргументы:
            user_id: идентификатор связанного пользователя или ``None``,
                если событие анонимное.
            event_type: короткое имя события, например login или logout.
            ip_address: IP-адрес клиента, если он известен.
            user_agent: строка User-Agent клиента, если она известна.
            details: дополнительная метаинформация о событии, которая хранится в JSONB.

        Возвращает:
            Сохранённый ORM-объект ``AuditLog``.
        """

        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def get_audit_logs_by_user_id(self, user_id: int) -> list[AuditLog]:
        """EN: Return all audit log rows related to a specific user.

        Args:
            user_id: Identifier of the user whose audit history is requested.

        Returns:
            List of ``AuditLog`` objects.

        RU: Возвращает все записи журнала аудита, связанные с конкретным пользователем.

        Аргументы:
            user_id: идентификатор пользователя, чья история аудита запрашивается.

        Возвращает:
            Список объектов ``AuditLog``.
        """

        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .all()
        )
