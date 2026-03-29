from datetime import datetime

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_refresh_token_by_user_id(self, user_id: int) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .first()
        )

    def create_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        ip_address: str,
        user_agent: str,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)

        return refresh_token