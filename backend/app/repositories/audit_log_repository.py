from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_audit_log(
        self,
        user_id: int | None,
        event_type: str,
        ip_address: str | None,
        user_agent: str | None,
        details: dict,
    ) -> AuditLog:
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
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .all()
        )