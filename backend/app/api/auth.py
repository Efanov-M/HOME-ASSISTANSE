from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (LoginRequest, 
                              TokenResponse, 
                              RegisterRequest, 
                              RefreshRequest, 
                              AccessTokenResponse, 
                              LogoutRequest,
                              MessageResponse,
                              PasswordResetRequest,
                              PasswordResetConfirmRequest)
from app.schemas.user import UserResponse, MeResponse
from app.services.auth_service import (login_user, 
                                       register_user, 
                                       refresh_access_token, 
                                       logout_user,
                                       request_password_reset,
                                       confirm_password_reset,
                                       get_current_user)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_endpoint(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """EN: Authenticate a user and return access/refresh tokens.

    Args:
        data: Login payload with email and password.
        request: FastAPI request object used to read client metadata.
        db: Active database session dependency.

    Returns:
        Token response produced by the auth service.

    RU: Аутентифицирует пользователя и возвращает access/refresh токены.

    Аргументы:
        data: payload входа с email и паролем.
        request: объект запроса FastAPI для чтения клиентских метаданных.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Ответ с токенами, который формирует auth service.
    """

    result = login_user(
        db=db,
        email=data.email,
        password=data.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return result


@router.post('/register', response_model=UserResponse)
def registr_endpoint(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """EN: Register a new user through the auth service.

    Args:
        data: Registration payload with email, password, and family name.
        db: Active database session dependency.

    Returns:
        Created user representation.

    RU: Регистрирует нового пользователя через auth service.

    Аргументы:
        data: payload регистрации с email, паролем и именем семьи.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Представление созданного пользователя.
    """

    result = register_user(
        db=db,
        email=data.email,
        password=data.password,
        family_name=data.family_name,
    )
    return result 


@router.post('/refresh', response_model=AccessTokenResponse)
def refresh_endpoint(
    data: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """EN: Exchange a valid refresh token for a new access token.

    Args:
        data: Request body with refresh token.
        request: FastAPI request object used to read client IP.
        db: Active database session dependency.

    Returns:
        Dictionary with a new access token.

    RU: Обменивает валидный refresh token на новый access token.

    Аргументы:
        data: тело запроса с refresh token.
        request: объект запроса FastAPI для чтения IP клиента.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Словарь с новым access token.
    """

    result = refresh_access_token(
        db=db,
        refresh_token=data.refresh_token,
        ip_address=request.client.host if request.client else None
    )

    return {"access_token": result}

@router.post('/logout', response_model=MessageResponse)
def logout_endpoint(
    data: LogoutRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """EN: Revoke a refresh token and finish the logout flow.

    Args:
        data: Request body with refresh token.
        request: FastAPI request object used to read client IP.
        db: Active database session dependency.

    Returns:
        Success message when logout completes.

    RU: Отзывает refresh token и завершает сценарий выхода из системы.

    Аргументы:
        data: тело запроса с refresh token.
        request: объект запроса FastAPI для чтения IP клиента.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Сообщение об успешном logout.
    """

    result = logout_user(
        db=db,
        refresh_token=data.refresh_token,
        ip_address=request.client.host if request.client else None
    )
    if result:

        return {"message": "Logout successful"} 
    
@router.post('/password-reset/request', response_model=MessageResponse)
def password_reset_request_endpoint(
    data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """EN: Start the password reset flow for the provided email.

    Args:
        data: Request body with user email.
        request: FastAPI request object used to read client metadata.
        db: Active database session dependency.

    Returns:
        Service message describing the result.

    RU: Запускает сценарий сброса пароля для указанного email.

    Аргументы:
        data: тело запроса с email пользователя.
        request: объект запроса FastAPI для чтения клиентских метаданных.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Сообщение сервиса о результате операции.
    """

    result = request_password_reset(
        db=db,
        email=data.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": result} 

@router.post('/password-reset/confirm', response_model=MessageResponse)
def password_reset_confirm_endpoint(
    data: PasswordResetConfirmRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """EN: Confirm password reset using reset token and a new password.

    Args:
        data: Request body with reset token and new password.
        request: FastAPI request object used to read client IP.
        db: Active database session dependency.

    Returns:
        Service message after successful password change.

    RU: Подтверждает сброс пароля по reset token и новому паролю.

    Аргументы:
        data: тело запроса с reset token и новым паролем.
        request: объект запроса FastAPI для чтения IP клиента.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Сообщение сервиса после успешной смены пароля.
    """

    result = confirm_password_reset(
        db=db,
        reset_token=data.reset_token,
        password=data.password,
        ip_address=request.client.host if request.client else None,
    )

    return {"message": result} 

@router.get('/me', response_model=MeResponse)
def get_me_endpoint(
    request: Request,
    db: Session = Depends(get_db)
):
    """EN: Return the current authenticated user from the bearer token.

    Args:
        request: FastAPI request object containing the Authorization header.
        db: Active database session dependency.

    Returns:
        Current authenticated user data.

    Raises:
        HTTPException: If the Authorization header is missing or malformed.

    RU: Возвращает текущего аутентифицированного пользователя по bearer token.

    Аргументы:
        request: объект запроса FastAPI с заголовком Authorization.
        db: активная сессия базы данных из dependency.

    Возвращает:
        Данные текущего аутентифицированного пользователя.

    Исключения:
        HTTPException: Если заголовок Authorization отсутствует или имеет неверный формат.
    """

    
    auth_header = request.headers.get("authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    parts = auth_header.split()

    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    scheme, token = parts

    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    result = get_current_user(
        db=db,
        token=token,
        ip_address=request.client.host if request.client else None,
    )
    return result
