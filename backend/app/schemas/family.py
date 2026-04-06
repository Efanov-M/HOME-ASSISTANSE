from pydantic import BaseModel



class FamilyResponse(BaseModel):
    """EN: Response schema with basic family information.

    RU: Схема ответа с базовой информацией о семье.
    """

    id: int
    name: str
