from datetime import datetime

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_token_hash_by_user_id(self, user_id: int) -> str | None:
        return (
            self.db.query(PasswordResetToken.token_hash)
            .filter(PasswordResetToken.user_id == user_id)
            .scalar()
        )

    def create_password_reset_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        password_reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.db.add(password_reset_token)
        self.db.commit()
        self.db.refresh(password_reset_token)

        return password_reset_token

    def get_password_reset_token_by_hash(
        self,
        token_hash: str,
    ) -> PasswordResetToken | None:
        return (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )
    
    def mark_token_as_used(self, token_hash: str) -> PasswordResetToken | None:
        token = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
             )

        if token is None:
            return None

        token.used_at = datetime.now()

        self.db.commit()
        self.db.refresh(token)

        return token

        
