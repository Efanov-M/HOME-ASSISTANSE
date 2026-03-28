План файлов и модулей для реализации этого ТЗ

Сейчас дам тебе прикладную структуру проекта, по которой уже можно начинать писать код.

⸻

Предлагаемая структура

backend/
└── app/
    ├── core/
    │   ├── config.py
    │   ├── security.py
    │   └── database.py
    │
    ├── models/
    │   ├── family.py
    │   ├── user.py
    │   ├── refresh_token.py
    │   ├── password_reset_token.py
    │   └── audit_log.py
    │
    ├── schemas/
    │   ├── auth.py
    │   ├── user.py
    │   └── family.py
    │
    ├── repositories/
    │   ├── family_repository.py
    │   ├── user_repository.py
    │   ├── refresh_token_repository.py
    │   ├── password_reset_repository.py
    │   └── audit_log_repository.py
    │
    ├── services/
    │   └── auth_service.py
    │
    ├── api/
    │   └── auth.py
    │
    └── main.py

⸻

Что делает каждый слой

Это нужно понять до написания кода.

⸻

1. models/

Это модели БД.

Здесь описывается:
 • как выглядят таблицы в Python
 • какие поля есть
 • какие типы
 • какие связи

⸻

1. schemas/

Это схемы входа и выхода API.

Здесь описывается:
 • что принимает endpoint
 • что возвращает endpoint
 • какие поля валидируются

Например:
 • RegisterRequest
 • LoginRequest
 • TokenResponse
 • MeResponse

⸻

1. repositories/

Это слой работы с БД.

Здесь должна быть логика типа:
 • создать пользователя
 • найти пользователя по email
 • сохранить refresh token
 • отозвать refresh token
 • создать audit log

То есть:

repository = “чистая работа с таблицами”

⸻

1. services/

Это бизнес-логика.

Именно здесь ты собираешь сценарии:
 • register
 • login
 • refresh
 • logout
 • password reset

То есть:

service = “что система делает по шагам”

⸻

1. api/

Это HTTP-слой.

Только:
 • endpoint
 • принять запрос
 • вызвать service
 • вернуть ответ

Здесь нельзя писать:
 • SQL
 • hash-пароля
 • JWT-логику
 • сложную бизнес-логику

⸻

1. core/

Это базовая инфраструктура приложения.

⸻

config.py

Настройки:
 • DATABASE_URL
 • JWT_SECRET
 • ACCESS_TOKEN_EXPIRE_MINUTES
 • REFRESH_TOKEN_EXPIRE_DAYS

⸻

security.py

Безопасность:
 • hash password
 • verify password
 • create access token
 • create refresh token
 • hash refresh token
 • hash reset token

⸻

database.py

Подключение к PostgreSQL:
 • engine
 • session
 • base model

⸻

Что именно должно быть в каждом файле

Теперь уже совсем прикладно.

⸻

models/family.py

Модель families

Поля:
 • id
 • name
 • created_at
 • created_by

⸻

models/user.py

Модель users

Поля:
 • id
 • email
 • password_hash
 • role
 • is_active
 • family_id
 • created_at
 • updated_at

⸻

models/refresh_token.py

Модель refresh_tokens

Поля:
 • id
 • user_id
 • token_hash
 • expires_at
 • revoked_at
 • created_at
 • ip_address
 • user_agent

⸻

models/password_reset_token.py

Модель password_reset_tokens

Поля:
 • id
 • user_id
 • token_hash
 • expires_at
 • used_at
 • created_at

⸻

models/audit_log.py

Модель audit_logs

Поля:
 • id
 • user_id
 • event_type
 • ip_address
 • user_agent
 • created_at
 • details

⸻

Схемы (schemas/)

⸻

schemas/auth.py

Здесь должны быть схемы:

Request
 • RegisterRequest
 • LoginRequest
 • RefreshRequest
 • LogoutRequest
 • PasswordResetRequest
 • PasswordResetConfirmRequest

Response
 • RegisterResponse
 • TokenResponse
 • MessageResponse

⸻

schemas/user.py

Например:
 • CurrentUserResponse

⸻

schemas/family.py

Пока можно минимально или вообще не делать отдельно, если family возвращается только внутри register response.

⸻

Repository-файлы

⸻

repositories/user_repository.py

Должны быть функции/методы:
 • create_user
 • get_user_by_email
 • get_user_by_id
 • update_user_password
 • set_user_active_status

⸻

repositories/family_repository.py
 • create_family
 • get_family_by_id
 • list_family_users

⸻

repositories/refresh_token_repository.py
 • create_refresh_token
 • get_valid_refresh_token
 • revoke_refresh_token
 • revoke_all_user_refresh_tokens

⸻

repositories/password_reset_repository.py
 • create_password_reset_token
 • get_valid_password_reset_token
 • mark_password_reset_token_used
 • invalidate_user_reset_tokens

⸻

repositories/audit_log_repository.py
 • create_audit_log
 • list_user_audit_logs

⸻

Service-слой

⸻

services/auth_service.py

Это главный файл текущего этапа.

Здесь должны быть методы:
 • register_user
 • login_user
 • get_current_user
 • refresh_access_token
 • logout_user
 • request_password_reset
 • confirm_password_reset

Именно здесь будет собираться сценарий из нескольких repository-вызовов.

⸻

API-слой

⸻

api/auth.py

Здесь endpoint’ы:
 • POST /auth/register
 • POST /auth/login
 • GET /auth/me
 • POST /auth/refresh
 • POST /auth/logout
 • POST /auth/password-reset/request
 • POST /auth/password-reset/confirm

⸻

Порядок написания кода

Вот это уже тебе как рабочий план.

⸻

Этап 1

Создать инфраструктуру:
 • database.py
 • config.py
 • security.py

⸻

Этап 2

Создать все models/

⸻

Этап 3

Создать schemas/auth.py и schemas/user.py

⸻

Этап 4

Создать все repositories/

⸻

Этап 5

Создать auth_service.py

⸻

Этап 6

Создать api/auth.py

⸻

Этап 7

Подключить всё в main.py

⸻

Как не запутаться

Твоя ошибка будет, если ты начнёшь так:
 • сначала endpoint
 • потом в нём SQL
 • потом там же JWT
 • потом там же hash пароля

Так делать нельзя.

Правильная цепочка:

API -> Service -> Repository -> DB

⸻

Что я рекомендую начать писать первым

Самый правильный старт:

Шаг 1

database.py

Шаг 2

models/

Шаг 3

user_repository.py и family_repository.py

Потому что без этого дальше auth всё равно не собрать.

⸻

Конкретный вывод

Да, всё выше — это одно ТЗ.
А то, что я дал сейчас, — это уже план реализации этого ТЗ по файлам.

⸻

Следующий шаг

Теперь уже логично не обсуждать абстракции, а зафиксировать первую практическую задачу на код.

Первая задача:

создать database.py и весь пакет models/

Если хочешь, следующим сообщением я подготовлю тебе отдельное маленькое ТЗ только на первый подшаг:
core/database.py + models/*
чтобы ты начал писать код не по всему модулю сразу, а по одному куску.
