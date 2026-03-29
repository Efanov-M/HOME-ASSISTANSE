from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self,email: str,password_hash: str,role: UserRole,family_id: int,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            family_id=family_id,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
    



# Для твоего auth-модуля логично иметь ещё такие методы.

# Поиск
# 	•	get_user_by_id(...)
# 	•	get_user_by_email(...)

# Создание
# 	•	create_user(...)

# Обновление
# 	•	update_user_password(...)
# 	•	set_user_active_status(...)

# Дополнительно позже
# 	•	update_user_role(...)
# 	•	update_user_family(...)
# 	•	delete_user(...) — возможно, но не факт, что нужен в лоб