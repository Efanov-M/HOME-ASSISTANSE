from datetime import datetime,timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """EN: Repository for low-level work with ``refresh_tokens`` data.

    It keeps token-related SQLAlchemy operations in one place
    so auth logic stays cleaner in higher layers.

    RU: Репозиторий для низкоуровневой работы с данными ``refresh_tokens``.

    Он собирает token-related операции SQLAlchemy в одном месте,
    чтобы auth-логика в верхних слоях оставалась чище.
    """

    def __init__(self, db: Session):
        """EN: Save the session object that all repository methods will use.

        Args:
            db: Active SQLAlchemy session used for token queries and writes.

        RU: Сохраняет объект Session, через который будут работать все методы репозитория.

        Аргументы:
            db: активная SQLAlchemy-сессия для запросов и записи токенов.
        """

        self.db = db

    def get_refresh_token_by_user_id(self, user_id: int) -> RefreshToken | None:
        """EN: Return the first refresh token record for a user or ``None``.

        Args:
            user_id: Identifier of the user whose token is being searched.

        Returns:
            ``RefreshToken`` object or ``None``.

        RU: Возвращает первую запись refresh token пользователя или ``None``.

        Аргументы:
            user_id: идентификатор пользователя, чей токен ищется.

        Возвращает:
            Объект ``RefreshToken`` или ``None``.
        """

        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .first()
        )

    def get_refresh_token_by_token_hash(self, token: str) -> RefreshToken | None:
        """EN: Find a refresh token row by its stored hash.

        Args:
            token: Hashed refresh token value stored in the database.

        Returns:
            Matching ``RefreshToken`` object or ``None``.

        RU: Ищет запись refresh token по сохранённому hash-значению.

        Аргументы:
            token: хеш refresh token, который хранится в базе данных.

        Возвращает:
            Найденный объект ``RefreshToken`` или ``None``.
        """

        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token)
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
        """EN: Create a refresh token record, save its hash, and return the ORM object.

        Args:
            user_id: Token owner identifier.
            token_hash: Hashed token value stored in the database.
            expires_at: Datetime when the token becomes invalid.
            ip_address: Client IP address from which the token was issued.
            user_agent: Client user-agent string.

        Returns:
            Saved ``RefreshToken`` ORM object.

        RU: Создаёт запись refresh token, сохраняет её hash и возвращает ORM-объект.

        Аргументы:
            user_id: идентификатор владельца токена.
            token_hash: хеш токена, который будет храниться в базе.
            expires_at: дата и время, после которых токен считается недействительным.
            ip_address: IP-адрес клиента, с которого был выдан токен.
            user_agent: строка User-Agent клиента.

        Возвращает:
            Сохранённый ORM-объект ``RefreshToken``.
        """

        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(refresh_token)
        

        return refresh_token


    def revoke_refresh_token(self, token_object: RefreshToken) -> RefreshToken:
        """EN: Mark an existing refresh token as revoked.

        The method does NOT perform any lookup or validation.
        It only updates the given ORM object.

        Args:
            token_object: Existing RefreshToken ORM object.

        Returns:
            Updated RefreshToken object.

        RU: Помечает переданный refresh token как отозванный.

        Метод НЕ выполняет поиск и проверки.
        Он только изменяет уже полученный ORM-объект.

        Аргументы:
            token_object: ORM-объект RefreshToken.

        Возвращает:
            Обновлённый объект RefreshToken.
        """

        token_object.revoked_at = datetime.now(timezone.utc)
        return token_object
