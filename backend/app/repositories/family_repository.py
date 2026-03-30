from sqlalchemy.orm import Session

from app.models.family import Family


class FamilyRepository:
    """EN: Repository for working with ``families`` table data.

    The repository isolates database access logic so higher layers
    do not have to build ORM queries directly.

    RU: Репозиторий для работы с данными таблицы ``families``.

    Репозиторий изолирует доступ к базе данных,
    чтобы верхним слоям не приходилось писать ORM-запросы напрямую.
    """

    def __init__(self, db: Session):
        """EN: Store the active SQLAlchemy session inside the repository.

        The repository will reuse this session in all its methods.

        Args:
            db: SQLAlchemy Session object used for queries, inserts, commits,
                and refreshing ORM entities inside this repository.

        RU: Сохраняет активную SQLAlchemy-сессию внутри репозитория.

        Дальше все методы этого репозитория будут работать через неё.

        Аргументы:
            db: объект Session от SQLAlchemy, через который репозиторий
                выполняет запросы, добавляет записи, делает commit
                и обновляет ORM-объекты.
        """

        self.db = db

    def get_family_by_name(self, name: str) -> Family | None:
        """EN: Return the first family found by name or ``None``.

        This method is useful when the caller wants one object
        and is okay with getting nothing if no match exists.

        Args:
            name: Family name used in the filter condition.

        Returns:
            The first matching ``Family`` object or ``None``.

        RU: Возвращает первую найденную семью по имени или ``None``.

        Такой метод удобен, когда вызывающему коду нужен один объект
        и нормально, если при отсутствии совпадения вернётся пустой результат.

        Аргументы:
            name: имя семьи, по которому строится фильтр.

        Возвращает:
            Первый найденный объект ``Family`` или ``None``.
        """

        return self.db.query(Family).filter(Family.name == name).first()

    def create_family(self, name: str) -> Family:
        """EN: Create a new family row, commit the transaction, and return it.

        After commit the method refreshes the ORM object
        so generated values from the database become available in Python.

        Args:
            name: Family name that will be written into the new row.

        Returns:
            Saved ``Family`` ORM object.

        RU: Создаёт новую запись семьи, фиксирует транзакцию и возвращает объект.

        После commit метод обновляет ORM-объект,
        чтобы значения, сгенерированные базой данных, были доступны в Python.

        Аргументы:
            name: имя семьи, которое будет записано в новую строку.

        Возвращает:
            Сохранённый ORM-объект ``Family``.
        """

        family = Family(name=name)

        self.db.add(family)
        self.db.commit()
        # ``refresh`` - это один из тех маленьких, но важных ORM-моментов:
        # после commit мы просим SQLAlchemy заново подтянуть данные из базы,
        # например сгенерированный первичный ключ.
        self.db.refresh(family)

        return family
