# Как FastAPI понимает, что именно прислал клиент и куда это положить

Разберём по порядку:

- что отправляет клиент
- что приходит в endpoint
- как FastAPI понимает, откуда брать `book_id`
- как он понимает, что `book_data` надо брать из body

Будем опираться на этот пример:

```py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


app = FastAPI()


class BookCreateRequest(BaseModel):
    title: str
    author: str
    year: int


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int


class MessageResponse(BaseModel):
    message: str


books_db = [
    {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932},
]


@app.get("/books", response_model=List[BookResponse])
def get_all_books():
    return books_db


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books", response_model=BookResponse)
def create_book(book_data: BookCreateRequest):
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
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(index)
            return {"message": "Книга успешно удалена"}

    raise HTTPException(status_code=404, detail="Книга не найдена")
```

1. Что именно отправляет клиент

Клиент отправляет HTTP-запрос.

У любого HTTP-запроса есть несколько частей:
 • метод
 • путь
 • заголовки
 • иногда query-параметры
 • иногда тело запроса

Разберём это на примерах.

Пример 1. Получить все книги

Клиент отправляет:

GET /books HTTP/1.1
Host: 127.0.0.1:8000

Что здесь важно:
 • GET — метод
 • /books — путь
 • тела запроса нет

То есть клиент просто говорит:

дай мне все книги

⸻

Пример 2. Получить одну книгу по ID

Клиент отправляет:

GET /books/2 HTTP/1.1
Host: 127.0.0.1:8000

Что здесь важно:
 • GET — метод
 • /books/2 — путь
 • внутри пути уже зашит идентификатор книги

То есть клиент говорит:

дай мне книгу с ID = 2

⸻

Пример 3. Создать книгу

Клиент отправляет:

POST /books HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}

Что здесь важно:
 • POST — метод
 • /books — путь
 • в теле запроса лежит JSON

То есть клиент говорит:

создай новую книгу
вот её данные

⸻

Пример 4. Удалить книгу

Клиент отправляет:

DELETE /books/2 HTTP/1.1
Host: 127.0.0.1:8000

Это означает:

удали книгу с ID = 2

⸻

1. Что именно приходит в endpoint

Теперь важный момент: что FastAPI передаёт в твою Python-функцию.

Вот endpoint:

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int):

Если клиент вызвал:

GET /books/2 HTTP/1.1
Host: 127.0.0.1:8000

то FastAPI передаст в функцию:

book_id = 2

То есть endpoint получает уже готовое значение.

⸻

Другой пример:

@app.post("/books", response_model=BookResponse)
def create_book(book_data: BookCreateRequest):

Если клиент отправил:

POST /books HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}

то FastAPI создаст объект BookCreateRequest и передаст его в функцию как book_data.

То есть внутри endpoint ты уже получаешь не “сырой JSON”, а нормальный Python-объект.

⸻

1. Как FastAPI понимает, что book_id надо брать из URL

Разберём этот код:

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int):

Вот здесь происходит очень важная связка:

Шаг 1. FastAPI смотрит на путь

"/books/{book_id}"

Фигурные скобки означают:

это переменная часть URL

То есть FastAPI понимает:

вместо {book_id} придёт какое-то конкретное значение

Например:
 • /books/1
 • /books/2
 • /books/500

⸻

Шаг 2. FastAPI смотрит на имя параметра функции

def get_book_by_id(book_id: int):

Имя параметра функции:

book_id

совпадает с именем в пути:

{book_id}

⸻

Шаг 3. FastAPI связывает их

То есть FastAPI рассуждает так:

в URL есть переменная {book_id}
в функции есть аргумент book_id
значит значение из URL нужно передать в этот аргумент

⸻

Шаг 4. FastAPI приводит тип

Ты написал:

book_id: int

значит FastAPI пытается привести значение к числу.

Если клиент отправил:

GET /books/2 HTTP/1.1

то FastAPI сделает:

book_id = 2

Если клиент отправил:

GET /books/abc HTTP/1.1

то FastAPI не сможет превратить abc в int и вернёт ошибку.

⸻

Важный вывод

FastAPI понимает, что book_id надо брать из URL, потому что:
 1. в маршруте есть {book_id}
 2. в функции есть аргумент book_id
 3. имя совпадает

⸻

1. Как FastAPI понимает, что book_data надо брать из body

Теперь другой endpoint:

@app.post("/books", response_model=BookResponse)
def create_book(book_data: BookCreateRequest):

Здесь уже другой механизм.

⸻

Что видит FastAPI

FastAPI видит, что у функции есть аргумент:

book_data: BookCreateRequest

И тип этого аргумента — Pydantic-модель, то есть класс, унаследованный от BaseModel.

class BookCreateRequest(BaseModel):
    title: str
    author: str
    year: int

⸻

Что FastAPI из этого понимает

Он рассуждает так:

если аргумент — это Pydantic-модель,
значит данные для него нужно брать из тела запроса

⸻

Как это выглядит на практике

Клиент отправляет:

POST /books HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}

FastAPI:
 1. читает JSON из body
 2. проверяет, что там есть:
 • title
 • author
 • year
 3. проверяет типы:
 • title — строка
 • author — строка
 • year — число
 4. создаёт объект BookCreateRequest
 5. передаёт его в endpoint

⸻

Что endpoint получает внутри

Внутри функции ты работаешь уже так:

book_data.title
book_data.author
book_data.year

А не руками достаёшь поля из словаря.

⸻

Важный вывод

FastAPI понимает, что book_data надо брать из body, потому что:
 • это аргумент функции
 • его тип — Pydantic-модель (BookCreateRequest)

⸻

1. Разница между path parameter и body на одном примере

Сравним два endpoint.

Пример path parameter

@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):

Откуда берётся book_id

Из URL:

GET /books/2 HTTP/1.1

⸻

Пример body

@app.post("/books")
def create_book(book_data: BookCreateRequest):

Откуда берётся book_data

Из тела запроса:

{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}

⸻

1. Что будет, если клиент пришлёт неправильные данные в body

Например, клиент отправил:

POST /books HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "title": "Dune",
  "author": "Frank Herbert"
}

То есть забыл year.

FastAPI увидит, что схема требует:

class BookCreateRequest(BaseModel):
    title: str
    author: str
    year: int

И поймёт:

поле year обязательно, а его нет

В этом случае endpoint вообще не будет вызван.
FastAPI сам вернёт клиенту ошибку валидации.

⸻

Это очень важный момент

FastAPI может не пустить мусор в твою функцию.

То есть функция create_book(...) начинает работать только тогда, когда данные уже прошли базовую проверку структуры.

⸻

1. Что будет, если book_id неправильный

Например, клиент отправил:

GET /books/abc HTTP/1.1
Host: 127.0.0.1:8000

А у тебя:

def get_book_by_id(book_id: int):

FastAPI попытается сделать:

book_id = int("abc")

Это невозможно.

И снова endpoint не будет вызван — FastAPI вернёт ошибку.

⸻

1. Как FastAPI отличает body от обычных простых параметров

Это важный практический момент.

Правило очень простое

Если параметр — Pydantic-модель

FastAPI считает, что это body.

Пример:

book_data: BookCreateRequest

⸻

Если параметр совпадает с {...} в пути

FastAPI считает, что это path parameter.

Пример:

@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):

⸻

Если параметр простой и не в пути

Обычно FastAPI будет считать его query-параметром.

Пример:

@app.get("/books")
def search_books(year: int):

Тогда клиент должен вызвать:

GET /books?year=2020 HTTP/1.1

⸻

1. Небольшой дополнительный пример с query parameter

@app.get("/books/search")
def search_books(year: int):
    return {"year": year}

Если клиент отправит:

GET /books/search?year=2020 HTTP/1.1
Host: 127.0.0.1:8000

то FastAPI передаст в функцию:

year = 2020

⸻

Что важно понять

FastAPI смотрит на контекст параметра:
 • есть ли он в пути?
 • является ли он Pydantic-схемой?
 • является ли он обычным простым параметром?

И по этому решает, откуда его брать.

⸻

1. Визуальная схема: как FastAPI распределяет параметры

Путь

@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):

Берётся из URL:

/books/2 → book_id = 2

⸻

Тело

@app.post("/books")
def create_book(book_data: BookCreateRequest):

Берётся из body:

{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965
}

⸻

Query

@app.get("/books/search")
def search_books(year: int):

Берётся из query string:

/books/search?year=2020

⸻

1. Что здесь важно запомнить

FastAPI не читает твои мысли

Он ориентируется на вполне конкретные признаки:

Path

Совпадение имени параметра с {...} в URL.

Body

Параметр типа BaseModel.

Query

Обычные параметры, не найденные в path и не являющиеся body-моделью.

⸻

1. Самая короткая выжимка

- Если параметр указан в пути как `{book_id}`, FastAPI берёт его из URL.
- Если параметр имеет тип Pydantic-модели, FastAPI берёт его из body.
- Если параметр простой (`int`, `str`, `bool`) и не указан в пути, FastAPI обычно берёт его из query.

⸻

1. Мини-таблица для запоминания

Что в функции Откуда FastAPI возьмёт
book_id: int и путь "/books/{book_id}" из URL path
book_data: BookCreateRequest из body
year: int при пути "/books/search" из query

⸻

1. Что логично разобрать следующим шагом

Теперь следующий правильный шаг — объяснить так же подробно:
 • что такое response_model
 • зачем он нужен
 • почему FastAPI не просто возвращает “что угодно”
 • как он фильтрует и приводит ответ

Это следующий кирпичик после понимания входных параметров.
