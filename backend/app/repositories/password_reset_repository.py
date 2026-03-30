from datetime import datetime

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    """EN: Repository for database operations on ``password_reset_tokens``.

    This class keeps reset-token queries together:
    create, search, read hash values, and mark tokens as used.

    RU: Репозиторий для операций с базой данных над ``password_reset_tokens``.

    Этот класс держит запросы к reset-token в одном месте:
    создание, поиск, чтение hash-значений и пометка токенов как использованных.
    """

    def __init__(self, db: Session):
        """EN: Store the active session used for password reset token queries.

        Args:
            db: Active SQLAlchemy session used by this repository.

        RU: Сохраняет активную сессию, через которую выполняются запросы к токенам сброса.

        Аргументы:
            db: активная SQLAlchemy-сессия, через которую работает репозиторий.
        """

        self.db = db

    def get_token_hash_by_user_id(self, user_id: int) -> str | None:
        """EN: Return only the token hash for a user or ``None``.

        Notice that this query asks not for the whole ORM object,
        but for one scalar value from one column.

        Args:
            user_id: Identifier of the user whose token hash is requested.

        Returns:
            Token hash string or ``None``.

        RU: Возвращает только hash токена пользователя или ``None``.

        Обрати внимание: этот запрос просит не целый ORM-объект,
        а одно скалярное значение из одной колонки.

        Аргументы:
            user_id: идентификатор пользователя, для которого ищется hash токена.

        Возвращает:
            Строку с hash токена или ``None``.
        """

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
        """EN: Create a password reset token row and return the saved ORM object.

        Args:
            user_id: User identifier.
            token_hash: Hashed reset token value.
            expires_at: Expiration datetime for the reset token.

        Returns:
            Saved ``PasswordResetToken`` ORM object.

        RU: Создаёт запись токена сброса пароля и возвращает сохранённый ORM-объект.

        Аргументы:
            user_id: идентификатор пользователя.
            token_hash: хеш токена сброса пароля.
            expires_at: дата и время истечения токена.

        Возвращает:
            Сохранённый ORM-объект ``PasswordResetToken``.
        """

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
        """EN: Find a reset token row by its hash and return it or ``None``.

        Args:
            token_hash: Hash value used to find the row.

        Returns:
            Matching ``PasswordResetToken`` or ``None``.

        RU: Ищет запись токена по его hash и возвращает объект или ``None``.

        Аргументы:
            token_hash: hash-значение, по которому ищется запись.

        Возвращает:
            Найденный ``PasswordResetToken`` или ``None``.
        """

        return (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )

    def mark_token_as_used(self, token_hash: str) -> PasswordResetToken | None:
        """EN: Mark a reset token as used if it exists and return the updated row.

        The method first loads the token, then changes the ``used_at`` field,
        commits the transaction, and refreshes the ORM object.

        Args:
            token_hash: Hash of the token that should be marked as used.

        Returns:
            Updated ``PasswordResetToken`` object or ``None``.

        RU: Помечает токен использованным, если он найден, и возвращает обновлённую запись.

        Метод сначала загружает токен, затем меняет поле ``used_at``,
        фиксирует транзакцию и обновляет ORM-объект.

        Аргументы:
            token_hash: hash токена, который нужно пометить как использованный.

        Возвращает:
            Обновлённый объект ``PasswordResetToken`` или ``None``.
        """

        token = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )

        if token is None:
            return None

        # Эта строка - момент "изменения состояния":
        # сначала меняется ORM-объект в памяти,
        # и только после ``commit`` это изменение становится постоянным в БД.
        token.used_at = datetime.now()

        self.db.commit()
        self.db.refresh(token)

        return token
