# Минимум:
#  • RegisterRequest
#  • LoginRequest
#  • RefreshRequest
#  • LogoutRequest
#  • PasswordResetRequest
#  • PasswordResetConfirmRequest
#  • TokenResponse
#  • MessageResponse
from pydantic import BaseModel



class RegisterRequest(BaseModel):
    """EN: Request schema for user registration.

    RU: Схема запроса для регистрации пользователя.
    """

    email: str
    password: str
    family_name: str

class LoginRequest(BaseModel):
    """EN: Request schema for user login.

    RU: Схема запроса для входа пользователя.
    """
        
    email: str
    password: str

class RefreshRequest(BaseModel):
    """EN: Request schema for access-token refresh.

    RU: Схема запроса для обновления access token.
    """

    refresh_token: str

class LogoutRequest(BaseModel):
    """EN: Request schema for logout by refresh token.

    RU: Схема запроса для выхода из системы по refresh token.
    """

    refresh_token: str
        
class PasswordResetRequest(BaseModel):
    """EN: Request schema for starting password reset flow.

    RU: Схема запроса для запуска сценария сброса пароля.
    """

    email: str

class PasswordResetConfirmRequest(BaseModel):
    """EN: Request schema for confirming password reset.

    RU: Схема запроса для подтверждения сброса пароля.
    """

    reset_token: str
    password: str          # тут подразумевается новый пароль 

class TokenResponse(BaseModel):
    """EN: Response schema containing access and refresh tokens.

    RU: Схема ответа, содержащая access и refresh токены.
    """

    access_token: str
    refresh_token: str

class MessageResponse(BaseModel):
    """EN: Generic response schema with a text message.

    RU: Универсальная схема ответа с текстовым сообщением.
    """

    message: str

class AccessTokenResponse(BaseModel):
    """EN: Response schema containing only a new access token.

    RU: Схема ответа, содержащая только новый access token.
    """

    access_token: str
