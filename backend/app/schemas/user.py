from pydantic import BaseModel, ConfigDict
from app.models.user import UserRole





class UserResponse (BaseModel):
    """EN: Response schema for a user returned by auth endpoints.

    RU: Схема ответа с пользователем, которую возвращают auth endpoint.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: UserRole
    is_active: bool
    family_id: int



class MeResponse(BaseModel):
    """EN: Response schema for the current authenticated user.

    RU: Схема ответа для текущего аутентифицированного пользователя.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: UserRole
    is_active: bool
    family_id: int # на данном этапе по совету ИИ оставляю пока так как есть, при разростании проекта буду добавлять 
