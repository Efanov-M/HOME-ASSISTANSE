# Минимальные методы:

# - create_task
# - get_task_by_id
# - list_tasks
# - update_task
# - delete_task

# Дополнительно допустимо:

# - list_personal_tasks
# - list_family_tasks

# Требования к repository:

# - не решает бизнес-логику;
# - не проверяет права;
# - не определяет, кто может видеть задачу;
# - не знает, что такое “текущий пользователь”;
# - только читает и пишет данные.

# Критерий готовности блока:

# - repository умеет выполнять базовые CRUD-операции для задач;
# - методы не содержат доменной логики доступа.
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


class TaskRepository:
    """Репозиторий для работы с задачами.

    Репозиторий отвечает только за создание, чтение, изменение и удаление
    ORM-объектов задач. Бизнес-логика доступа и проверок в нём не размещается.

    :param db: Активная SQLAlchemy-сессия.
    :type db: Session
    :return: Ничего не возвращает.
    :rtype: None
    """

    def __init__(self, db: Session):
        """Сохраняет активную сессию базы данных.

        :param db: Активная SQLAlchemy-сессия.
        :type db: Session
        :return: Ничего не возвращает.
        :rtype: None
        """
        self.db = db

    def create_task(
        self,
        title: str,
        description: str | None,
        status: TaskStatus,
        is_family_task: bool,
        created_by: int,
        assigned_to: int | None,
        family_id: int | None,
        due_date: datetime | None,
    ) -> Task:
        """Создаёт ORM-объект задачи и добавляет его в текущую сессию.

        Метод не делает commit и не решает бизнес-правила.
        Он только собирает объект Task из уже подготовленных данных
        и помещает его в SQLAlchemy-сессию.

        :param title: Краткое название задачи.
        :type title: str
        :param description: Подробное описание задачи или None.
        :type description: str | None
        :param status: Статус задачи.
        :type status: TaskStatus
        :param is_family_task: Признак семейной задачи.
        :type is_family_task: bool
        :param created_by: Идентификатор пользователя, создавшего задачу.
        :type created_by: int
        :param assigned_to: Идентификатор исполнителя или None.
        :type assigned_to: int | None
        :param family_id: Идентификатор семьи или None.
        :type family_id: int | None
        :param due_date: Дедлайн задачи или None.
        :type due_date: datetime | None
        :return: Новый ORM-объект задачи, добавленный в сессию.
        :rtype: Task
        """
        task = Task(
            title=title,
            description=description,
            status=status,
            is_family_task=is_family_task,
            created_by=created_by,
            assigned_to=assigned_to,
            family_id=family_id,
            due_date=due_date,
        )
        self.db.add(task)
        return task

    def get_task_by_id(self, id: int):
        return self.db.query(Task).filter(Task.id == id).first()
    

    def list_tasks(self,id: int):
        return self.db.query(Task).filter(Task.id == id).all()
    

    def update_task(self, )