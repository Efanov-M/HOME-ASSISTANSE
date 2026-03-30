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
        """EN: Create a new user, commit it, and return the saved ORM object.

        The method prepares a ``User`` instance, adds it to the session,
        commits the transaction, and then refreshes the object from the database.

        Args:
            email: User email.
            password_hash: Already prepared password hash, not a raw password.
            role: Role value from ``UserRole`` enum.
            family_id: Identifier of the family this user belongs to.

        Returns:
            Saved ``User`` ORM object.

        RU: Создаёт нового пользователя, делает commit и возвращает сохранённый ORM-объект.

        Метод собирает экземпляр ``User``, добавляет его в сессию,
        фиксирует транзакцию, а затем обновляет объект данными из базы.

        Аргументы:
            email: email пользователя.
            password_hash: уже подготовленный хеш пароля, а не сырой пароль.
            role: значение роли из enum ``UserRole``.
            family_id: идентификатор семьи, к которой относится пользователь.

        Возвращает:
            Сохранённый ORM-объект ``User``.
        """

        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            family_id=family_id,
        )

        self.db.add(user)
        self.db.commit()
        # ``commit`` фиксирует транзакцию, но именно ``refresh`` помогает
        # объекту в памяти Python догнать итоговое состояние записи в базе.
        self.db.refresh(user)

        return user
