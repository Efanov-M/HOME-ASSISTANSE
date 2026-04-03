from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    """EN: Repository responsible for reading and writing ``users`` table data.

    The main idea is simple: SQLAlchemy query details live here,
    while business decisions should stay in services.

    RU: Репозиторий, который отвечает за чтение и запись данных таблицы ``users``.

    Основная идея простая: детали SQLAlchemy-запросов живут здесь,
    а бизнес-решения должны оставаться в сервисном слое.
    """

    def __init__(self, db: Session):
        """EN: Accept the active SQLAlchemy session for this repository.

        Every method will use the same session object passed from outside.

        Args:
            db: Active SQLAlchemy session shared by repository methods.

        RU: Принимает активную SQLAlchemy-сессию для этого репозитория.

        Каждый метод дальше будет работать через один и тот же объект Session,
        который передан снаружи.

        Аргументы:
            db: активная SQLAlchemy-сессия, общая для методов репозитория.
        """

        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """EN: Find a user by email and return ``User`` or ``None``.

        This is a common lookup for authentication flows,
        because email usually acts as a unique identifier.

        Args:
            email: Email value used to search in the ``users`` table.

        Returns:
            Matching ``User`` object or ``None``.

        RU: Ищет пользователя по email и возвращает ``User`` или ``None``.

        Это типичный запрос для сценариев аутентификации,
        потому что email обычно выступает уникальным идентификатором.

        Аргументы:
            email: значение email, по которому ищется запись в таблице ``users``.

        Возвращает:
            Найденный объект ``User`` или ``None``.
        """

        return self.db.query(User).filter(User.email == email).first()
    

    def get_user_by_id(self, id: int) -> User | None:
        """EN: Return a user by primary key or ``None`` if it does not exist.

        Args:
            id: User identifier from the ``users`` table.

        Returns:
            Matching ``User`` object or ``None``.

        RU: Возвращает пользователя по первичному ключу или ``None``, если записи нет.

        Аргументы:
            id: идентификатор пользователя из таблицы ``users``.

        Возвращает:
            Найденный объект ``User`` или ``None``.
        """

        return self.db.query(User).filter(User.id == id).first()


    def create_user(
        self,
        email: str,
        password_hash: str,
        role: UserRole,
        family_id: int,
    ) -> User:
        """EN: Create a new user instance and add it to the current session.

    The method prepares a ``User`` instance and adds it to the session.
    The transaction is NOT committed here — this must be handled at the service layer.

    Args:
        email: User email.
        password_hash: Already prepared password hash, not a raw password.
        role: Role value from ``UserRole`` enum.
        family_id: Identifier of the family this user belongs to.

    Returns:
        New ``User`` ORM object added to the session (not yet committed).

    RU: Создаёт нового пользователя и добавляет его в текущую сессию.

        Метод создаёт экземпляр ``User`` и добавляет его в сессию.
        Фиксация транзакции (commit) здесь НЕ выполняется — это ответственность сервисного слоя.

    Аргументы:
        email: email пользователя.
        password_hash: уже подготовленный хеш пароля, а не сырой пароль.
        role: значение роли из enum ``UserRole``.
        family_id: идентификатор семьи, к которой относится пользователь.

    Возвращает:
        Новый ORM-объект ``User``, добавленный в сессию (ещё не сохранён в БД).
    """
        

        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            family_id=family_id,
        )

        self.db.add(user)
        return user

    def update_user_password(self, user_id: int, password_hash: str) -> User | None:
        """EN: Update the password hash for an existing user.

        Args:
            user_id: Identifier of the user whose password should be changed.
            password_hash: New prepared password hash.

        Returns:
            Updated ``User`` object or ``None`` if the user does not exist.

        RU: Обновляет хеш пароля существующего пользователя.

        Аргументы:
            user_id: идентификатор пользователя, чей пароль нужно изменить.
            password_hash: новый подготовленный хеш пароля.

        Возвращает:
            Обновлённый объект ``User`` или ``None``, если пользователь не найден.
        """

        user = self.get_user_by_id(user_id)

        if not user:
            return None
    
        user.password_hash = password_hash
        
        return user
    
    def set_user_active_status(self, user_id: int, status: bool) -> User | None:
        """EN: Change the active status flag for a user.

        Args:
            user_id: Identifier of the user to update.
            status: New boolean value for ``is_active``.

        Returns:
            Updated ``User`` object or ``None`` if the user does not exist.

        RU: Меняет признак активности пользователя.

        Аргументы:
            user_id: идентификатор пользователя для обновления.
            status: новое булево значение для поля ``is_active``.

        Возвращает:
            Обновлённый объект ``User`` или ``None``, если пользователь не найден.
        """

        user = self.get_user_by_id(user_id)

        if not user:
            return None
        
        user.is_active = status
        return user



