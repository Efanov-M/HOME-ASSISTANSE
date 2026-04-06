
# Полный учебный пример

```py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


app = FastAPI()


class BookCreateRequest(BaseModel):
    """
    Описывает входные данные для создания новой книги.

    Эта схема нужна для проверки тела POST-запроса.
    Клиент обязан передать название, автора и год издания.

    :param title: Название книги.
    :type title: str
    :param author: Автор книги.
    :type author: str
    :param year: Год издания книги.
    :type year: int
    :return: Ничего не возвращает. Используется как схема входных данных.
    :rtype: None
    """

    title: str
    author: str
    year: int


class BookResponse(BaseModel):
    """
    Описывает данные, которые backend возвращает клиенту о книге.

    Эта схема нужна для стандартизации ответа API.
    Она показывает, какие поля разрешено отдавать наружу.

    :param id: Уникальный идентификатор книги.
    :type id: int
    :param title: Название книги.
    :type title: str
    :param author: Автор книги.
    :type author: str
    :param year: Год издания книги.
    :type year: int
    :return: Ничего не возвращает. Используется как схема выходных данных.
    :rtype: None
    """

    id: int
    title: str
    author: str
    year: int


class MessageResponse(BaseModel):
    """
    Описывает простой текстовый ответ backend.

    Используется там, где не нужно возвращать объект книги,
    а нужно только сообщить результат операции.

    :param message: Текст сообщения для клиента.
    :type message: str
    :return: Ничего не возвращает. Используется как схема выходных данных.
    :rtype: None
    """

    message: str


# Учебное "хранилище" в памяти.
# В реальном проекте вместо этого будет база данных.
books_db = [
    {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932},
]


@app.get("/books", response_model=List[BookResponse])
def get_all_books():
    """
    Возвращает список всех книг.

    Эта функция показывает самый простой GET endpoint:
    клиент ничего не отправляет в теле запроса,
    а backend просто отдаёт все книги из хранилища.

    :return: Список книг.
    :rtype: list[BookResponse]
    """

    return books_db


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int):
    """
    Возвращает одну книгу по её идентификатору.

    Функция получает идентификатор из URL,
    ищет книгу в учебном хранилище
    и либо возвращает её, либо сообщает, что книга не найдена.

    :param book_id: Идентификатор книги из пути URL.
    :type book_id: int
    :return: Данные найденной книги.
    :rtype: BookResponse
    :raises HTTPException: Если книга с таким идентификатором не найдена.
    """

    for book in books_db:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books", response_model=BookResponse)
def create_book(book_data: BookCreateRequest):
    """
    Создаёт новую книгу и возвращает её клиенту.

    Функция принимает данные из тела POST-запроса,
    вычисляет новый идентификатор,
    формирует объект книги,
    сохраняет его в учебное хранилище
    и возвращает результат.

    :param book_data: Проверенные входные данные новой книги.
    :type book_data: BookCreateRequest
    :return: Созданная книга.
    :rtype: BookResponse
    """

    new_id = max(book["id"] for book in books_db) + 1 if books_db else 1

    new_book = {
        "id": new_id,
        "title": book_data.title,
        "author": book_data.author,
        "year": book_data.year,
    }

    books_db.append(new_book)
    return new_book


@app.delete("/books/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int):
    """
    Удаляет книгу по её идентификатору.

    Функция получает идентификатор из URL,
    ищет книгу в хранилище,
    удаляет её при нахождении
    и возвращает сообщение об успешной операции.

    :param book_id: Идентификатор книги, которую нужно удалить.
    :type book_id: int
    :return: Сообщение о результате удаления.
    :rtype: MessageResponse
    :raises HTTPException: Если книга с таким идентификатором не найдена.
    """

    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(index)
            return {"message": "Книга успешно удалена"}

    raise HTTPException(status_code=404, detail="Книга не найдена")
```

⸻

Теперь подробный разбор, как учитель

⸻

1. Импорты

```py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
```

Разберём по строкам.

>FastAPI

Это главный класс, который создаёт само приложение.

То есть строка ниже:

>app = FastAPI()

означает:

создай backend-приложение, которое умеет принимать HTTP-запросы

⸻

>HTTPException

Это специальный способ вернуть клиенту ошибку через FastAPI.

Например:
 • книга не найдена,
 • пользователь не найден,
 • токен невалиден.

То есть это не просто Python-ошибка “что-то сломалось”, а осмысленный HTTP-ответ с кодом ошибки.

⸻

>BaseModel

Это основа для Pydantic-схем.

Когда ты пишешь:

>class BookCreateRequest(BaseModel):

ты говоришь:

это не обычный класс Python,
а схема данных, которую FastAPI будет использовать для проверки входа

⸻

>List

Это тип “список”.

Нужно, когда endpoint возвращает не один объект, а много.

Например:

response_model=List[BookResponse]

означает:

backend должен вернуть список книг

⸻

## 2. Создание приложения

app = FastAPI()

Это точка старта.

Если очень просто:

app = FastAPI()

означает:

вот моё веб-приложение

Потом именно к этому объекту ты будешь “подвешивать” endpoint’ы:
 • @app.get(...)
 • @app.post(...)
 • @app.delete(...)

⸻

## 3. Схемы

Это очень важная часть.

⸻

```py
#BookCreateRequest

class BookCreateRequest(BaseModel):
    title: str
    author: str
    year: int
```

Эта схема описывает:

что клиент обязан прислать, когда хочет создать книгу

То есть для POST /books backend ждёт:
 • title
 • author
 • year

Если клиент не пришлёт одно из этих полей или пришлёт неверный тип, FastAPI сам вернёт ошибку.

Пример правильного тела запроса

```py
{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}
```

⸻

BookResponse

```py
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
```

Эта схема описывает:

как backend возвращает книгу наружу

Обрати внимание: здесь уже есть id, потому что когда книга создана или получена из хранилища, у неё должен быть идентификатор.

⸻

MessageResponse

```py
class MessageResponse(BaseModel):
    message: str
```

Это простая схема ответа для случаев, когда не нужен целый объект, а нужно просто сообщить результат.

Например:

```py
{
  "message": "Книга успешно удалена"
}
```

⸻

1. Учебная “база данных”

```py
books_db = [
    {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932},
]
```

Это не настоящая база данных.

Это просто список словарей в памяти.

Нужен он только для того, чтобы на учебном примере ты понял механику FastAPI, а не отвлекался сразу на PostgreSQL и SQLAlchemy.

То есть сейчас:

books_db = временное хранилище

В реальном проекте здесь было бы:
 • repository
 • service
 • database

⸻

1. Первый endpoint — получить все книги

```py
@app.get("/books", response_model=List[BookResponse])
def get_all_books():
    return books_db
```

Разбираем по частям.

⸻

>@app.get("/books", ...)

Это декоратор FastAPI.

Он означает:

если клиент прислал GET-запрос на /books,
нужно вызвать функцию get_all_books

⸻

Почему GET

Потому что мы получаем данные, а не создаём и не меняем.

⸻

Почему /books

Потому что endpoint относится к коллекции книг.

⸻

>response_model=List[BookResponse]

Это очень важная строка.

Она говорит FastAPI:

ответ должен быть списком объектов BookResponse

То есть backend обещает вернуть:
 • список,
 • в котором каждый элемент имеет поля:
 • id
 • title
 • author
 • year

⸻

Что делает функция

```py
def get_all_books():
    return books_db
```

Она просто возвращает все книги.

То есть запрос:

GET /books

даёт ответ:

```py
[
  {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
  {"id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932}
]
```

⸻

1. Второй endpoint — получить книгу по id

```py
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int):
```

Это уже следующий уровень.

⸻

Что значит "/books/{book_id}"

Это путь с параметром.

То есть если клиент пришёл на:
 • /books/1
 • /books/2
 • /books/100

FastAPI понимает:

вместо {book_id} нужно подставить конкретное число

⸻

book_id: int

Это означает:

параметр book_id должен быть числом

Если клиент пришлёт что-то вроде:

/books/abc

FastAPI сам поймёт, что это не int, и вернёт ошибку.

⸻

Что делает функция

Она перебирает книги и ищет совпадение по id.

Если нашла — возвращает книгу.
Если нет — вызывает:

>raise HTTPException(status_code=404, detail="Книга не найдена")

⸻

Почему именно HTTPException

Потому что это уже не “внутренний крах программы”, а нормальный API-ответ:

объект с таким id не найден

Клиент получит HTTP-статус 404.

⸻

## 7. Третий endpoint — создать книгу

```py
@app.post("/books", response_model=BookResponse)
def create_book(book_data: BookCreateRequest):
```

Это очень важный пример.

⸻

Почему POST

Потому что мы создаём новый объект.

⸻

Что такое book_data: BookCreateRequest

Вот здесь FastAPI делает магию, которая сначала кажется странной, а потом становится очень удобной.

Это означает:

возьми тело HTTP-запроса
проверь его по схеме BookCreateRequest
если всё нормально — передай в функцию как объект book_data

⸻

Что получает функция

Не сырой dict, а уже проверенный объект с полями:
 • book_data.title
 • book_data.author
 • book_data.year

⸻

Что делает функция

Шаг 1

Считает новый id:

>new_id = max(book["id"] for book in books_db) + 1 if books_db else 1

Логика:
 • если книги уже есть, берём максимальный id и прибавляем 1
 • если книг нет, начинаем с 1

⸻

Шаг 2

Создаёт новый словарь книги:

```py
new_book = {
    "id": new_id,
    "title": book_data.title,
    "author": book_data.author,
    "year": book_data.year,
}
```

⸻

Шаг 3

Добавляет книгу в “базу”:

>books_db.append(new_book)

⸻

Шаг 4

Возвращает созданную книгу:

>return new_book

⸻

Что клиент получит

Если клиент отправил:

```py
{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}

#то backend вернёт:

{
  "id": 3,
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}
```

⸻

1. Четвёртый endpoint — удалить книгу

```py
@app.delete("/books/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int):
```

⸻

Почему DELETE

Потому что мы удаляем объект.

⸻

Что делает функция

Она ищет книгу по id.

Если нашла:
 • удаляет её из списка
 • возвращает сообщение:

```py
{
  "message": "Книга успешно удалена"
}
```

Если не нашла:
> • возвращает 404

⸻

## 9. Что здесь уже можно понять про FastAPI

На одном этом примере ты уже видишь все базовые вещи.

⸻

А. Маршрутизация

FastAPI связывает:
 • HTTP-метод
 • путь
 • функцию

⸻

Б. Path parameters

Пример:

/books/{book_id}

⸻

В. Request schema

Пример:

BookCreateRequest

⸻

Г. Response schema

Примеры:

BookResponse
MessageResponse
List[BookResponse]

⸻

Д. Автоматическая валидация

FastAPI проверяет входные данные по схеме до того, как твоя логика начнёт работать.

⸻

Е. Ошибки через HTTPException

Ты можешь осмысленно вернуть клиенту:
 • не найдено
 • неверный запрос
 • и так далее

⸻

1. Как бы это выглядело в более взрослом проекте

Сейчас у нас всё в одном файле — это учебный упрощённый пример.

* ***В реальном проекте было бы так:***
* • schemas/book.py
* • repositories/book_repository.py
* • services/book_service.py
* • api/book.py

То есть:

endpoint → service → repository → db

Но для первого знакомства это было бы только мешающим перегрузом.

⸻

1. Что важно тебе понять именно сейчас

Если убрать всю “красоту”, то FastAPI в этом примере делает три главные вещи:

1. Принимает HTTP-запрос

Например:

POST /books

⸻

1. Превращает входные данные в понятный Python-объект

Через BookCreateRequest

⸻

1. Возвращает клиенту правильный ответ

Через BookResponse или MessageResponse

⸻

1. Что можно мысленно потрогать руками

Вот как ты должен это представлять.

⸻

Сценарий: создать книгу

Клиент отправил:

```py
{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}
```

FastAPI:
 • принял POST /books
 • проверил JSON по BookCreateRequest

Твоя функция:
 • создала новую книгу
 • добавила в хранилище

FastAPI:
 • завернул ответ в формат BookResponse

Клиент получил:

```py
{
  "id": 3,
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}
```

⸻

1. Самая важная мысль

FastAPI — это не “волшебство”, а просто очень удобный способ связать:

>HTTP ←→ Python-функции ←→ данные ←→ ответы
