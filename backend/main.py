"""Точка входа FastAPI-приложения.

Модуль собирает приложение в одном месте:
- создаёт объект FastAPI;
- подключает auth router;
- добавляет технический endpoint для проверки доступности сервиса.
"""

from fastapi import FastAPI

from app.api.auth import router as auth_router


app = FastAPI(
    title="Home Secretary API",
    description="HTTP API для backend-части проекта Home Secretary.",
    version="0.1.0",
)

app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Возвращает простой статус доступности приложения.

    Endpoint нужен для быстрой проверки, что сервер запущен,
    роутинг работает и приложение отвечает на HTTP-запросы.

    :return: Словарь с текстовым статусом приложения.
    :rtype: dict[str, str]
    """
    return {"status": "ok"}