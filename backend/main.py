"""Точка входа FastAPI-приложения.

Модуль:
- создаёт объект FastAPI;
- подключает auth router;
- добавляет глобальные обработчики исключений;
- предоставляет health endpoint.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.core.errors import (
    AuthError,
    AccessTokenNotFound,
    RefreshTokenNotFound,
    RefreshTokenRevoked,
    RefreshTokenExpired,
    RefreshTokenNoExpiry,
    ResetTokenNotFound,
    ResetTokenExpired,
    ResetTokenUsed,
    ResetTokenNoExpiry,
    RefreshUserBlocked,
    AccessUserBlocked,
    RefreshUserNotFound,
    AccessUserNotFound,
)


app = FastAPI(
    title="Home Secretary API",
    description="HTTP API для backend-части проекта Home Secretary.",
    version="0.1.0",
)


def get_auth_error_status_code(exc: AuthError) -> int:
    """Определяет HTTP-статус для auth-ошибки.

    :param exc: Экземпляр ошибки auth-слоя.
    :type exc: AuthError
    :return: HTTP-статус, соответствующий типу ошибки.
    :rtype: int
    """

    if isinstance(
        exc,
        (
            AccessTokenNotFound,
            RefreshTokenNotFound,
            RefreshTokenRevoked,
            RefreshTokenExpired,
            RefreshTokenNoExpiry,
            ResetTokenNotFound,
            ResetTokenExpired,
            ResetTokenUsed,
            ResetTokenNoExpiry,
        ),
    ):
        return 401

    if isinstance(exc, (RefreshUserBlocked, AccessUserBlocked)):
        return 403

    if isinstance(exc, (RefreshUserNotFound, AccessUserNotFound)):
        return 404

    return 400


@app.exception_handler(AuthError)
def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    """Преобразует доменные auth-ошибки в корректный HTTP-ответ.

    :param request: Текущий HTTP-запрос.
    :type request: Request
    :param exc: Ошибка auth-слоя.
    :type exc: AuthError
    :return: JSON-ответ с detail и корректным HTTP-статусом.
    :rtype: JSONResponse
    """

    status_code = get_auth_error_status_code(exc)

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Преобразует ValueError в контролируемый HTTP-ответ.

    :param request: Текущий HTTP-запрос.
    :type request: Request
    :param exc: Ошибка валидации или конфликта.
    :type exc: ValueError
    :return: JSON-ответ с detail и корректным HTTP-статусом.
    :rtype: JSONResponse
    """

    message = str(exc)

    if message in (
        "Пользователь с таким email уже существует",
        "Семья с таким именем уже существует",
    ):
        status_code = 409
    elif message == "Неверный пароль":
        status_code = 401
    else:
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={"detail": message},
    )


app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Возвращает простой статус доступности приложения.

    :return: Словарь со статусом приложения.
    :rtype: dict[str, str]
    """
    return {"status": "ok"}