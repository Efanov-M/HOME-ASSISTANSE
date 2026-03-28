
Техническое задание

Проект: Home Secretary

Модуль: Core Identity / Auth v1

⸻

1. Цель этапа

Реализовать базовое ядро системы, которое обеспечивает:
 • регистрацию пользователя
 • вход в систему
 • выпуск JWT access token
 • выпуск и хранение refresh token
 • обновление access token
 • logout с отзывом refresh token
 • восстановление пароля
 • получение данных текущего пользователя
 • журналирование событий безопасности

Этот этап является обязательной основой для всех следующих модулей:
 • organizer
 • calendar
 • finance
 • documents

⸻

1. Границы этапа

Входит в этап
 • модель families
 • модель users
 • модель refresh_tokens
 • модель password_reset_tokens
 • модель audit_logs
 • регистрация
 • логин
 • /auth/me
 • refresh
 • logout
 • password reset request
 • password reset confirm

Не входит в этап
 • email confirmation
 • 2FA
 • приглашения пользователей в семью
 • управление несколькими admin внутри family
 • изменение профиля
 • смена email
 • UI production-уровня
 • rate limiting
 • captcha
 • полноценная админ-панель

⸻

1. Текущая модель данных

3.1. Таблица families

Назначение: хранение семейной группы.

Поля:
 • id
 • name
 • created_at
 • created_by

⸻

3.2. Таблица users

Назначение: хранение пользователей системы.

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

3.3. Таблица refresh_tokens

Назначение: хранение refresh token с возможностью отзыва.

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

3.4. Таблица password_reset_tokens

Назначение: токены восстановления пароля.

Поля:
 • id
 • user_id
 • token_hash
 • expires_at
 • used_at
 • created_at

⸻

3.5. Таблица audit_logs

Назначение: аудит событий безопасности.

Поля:
 • id
 • user_id
 • event_type
 • ip_address
 • user_agent
 • created_at
 • details

⸻

1. Бизнес-правила

4.1. Общие правила
 1. Пользователь идентифицируется по email.
 2. Email должен быть уникальным.
 3. Пароль в БД хранится только как hash.
 4. Один пользователь на этапе v1 принадлежит только одной family.
 5. При регистрации создаётся новая family.
 6. Первый зарегистрированный пользователь этой family получает роль admin.
 7. Пользователь с is_active = false не может входить в систему.
 8. Refresh token хранится в БД только в виде hash.
 9. Reset token хранится в БД только в виде hash.
 10. Все чувствительные auth-события пишутся в audit_logs.

⸻

4.2. Правила токенов

Access token
 • короткоживущий
 • в БД не хранится
 • используется для доступа к защищённым endpoint’ам

Refresh token
 • долгоживущий
 • хранится в БД как hash
 • может быть отозван через revoked_at
 • используется для получения нового access token

Password reset token
 • одноразовый
 • после использования помечается через used_at
 • истёкший токен считается недействительным

⸻

1. Функциональные требования

⸻

FR-1. Регистрация пользователя

Назначение

Создать нового пользователя и новую семейную группу.

Входные данные
 • email
 • password
 • family_name

Логика

Система должна:
 1. проверить формат email
 2. проверить, что email ещё не существует
 3. проверить пароль по минимальным правилам
 4. создать запись в families
 5. захешировать пароль
 6. создать запись в users
 7. назначить роль admin
 8. привязать пользователя к новой family
 9. записать событие в audit_logs

Результат
 • пользователь создан
 • family создана
 • пользователь связан с family
 • пользователь может перейти к логину или сразу получить токены — это надо зафиксировать в реализации

Решение для v1

Для простоты рекомендую:
 • после регистрации сразу НЕ логинить автоматически
 • после регистрации пользователь отдельно делает /auth/login

Это упрощает логику и отладку.

⸻

FR-2. Логин

Назначение

Аутентифицировать пользователя и выдать токены.

Входные данные
 • email
 • password

Логика

Система должна:
 1. найти пользователя по email
 2. если пользователь не найден — вернуть auth error
 3. если пользователь неактивен — вернуть ошибку доступа
 4. сравнить пароль с password_hash
 5. при успешной проверке:
 • создать access token
 • создать refresh token
 • сохранить hash refresh token в refresh_tokens
 • записать IP и User-Agent
 • записать audit log

Результат
 • access token выдан
 • refresh token выдан
 • refresh token сохранён в БД как hash

⸻

FR-3. Получение текущего пользователя (/auth/me)

Назначение

Вернуть информацию о текущем аутентифицированном пользователе.

Логика

Система должна:
 1. принять access token
 2. проверить подпись и срок действия
 3. получить user_id из токена
 4. найти пользователя в users
 5. вернуть его основные данные

Возвращаемые поля

Минимум:
 • id
 • email
 • role
 • is_active
 • family_id
 • created_at

⸻

FR-4. Обновление access token (/auth/refresh)

Назначение

Выдать новый access token на основе валидного refresh token.

Входные данные
 • raw refresh token

Логика

Система должна:
 1. захешировать полученный refresh token
 2. найти запись в refresh_tokens
 3. проверить:
 • запись существует
 • revoked_at IS NULL
 • expires_at > now()
 4. проверить пользователя:
 • существует
 • активен
 5. выдать новый access token
 6. записать audit log

Допущение v1

В первой версии refresh token можно не ротировать.
То есть:
 • refresh token остаётся тем же
 • обновляется только access token

Это упрощает реализацию.

⸻

FR-5. Logout

Назначение

Отозвать текущий refresh token и завершить сессию.

Входные данные
 • raw refresh token

Логика

Система должна:
 1. захешировать refresh token
 2. найти запись в refresh_tokens
 3. если запись найдена и ещё не отозвана:
 • установить revoked_at = now()
 4. записать audit log

Результат
 • данный refresh token больше не может использоваться
 • access token доживёт до конца своего короткого срока

Это нормальная модель для JWT.

⸻

FR-6. Запрос на восстановление пароля

Назначение

Создать reset token.

Входные данные
 • email

Логика

Система должна:
 1. найти пользователя по email
 2. если пользователь найден:
 • создать raw reset token
 • сохранить его hash в password_reset_tokens
 • выставить expires_at
 • записать audit log
 3. если пользователь не найден:
 • всё равно вернуть нейтральный ответ
 • не раскрывать существование email

Ответ

Ответ должен быть одинаковый в обоих случаях.

⸻

FR-7. Подтверждение сброса пароля

Назначение

Установить новый пароль по reset token.

Входные данные
 • raw reset token
 • new_password

Логика

Система должна:
 1. захешировать токен
 2. найти запись в password_reset_tokens
 3. проверить:
 • существует
 • used_at IS NULL
 • expires_at > now()
 4. провалидировать новый пароль
 5. захешировать новый пароль
 6. обновить users.password_hash
 7. обновить users.updated_at
 8. установить used_at = now()
 9. записать audit log

Дополнительное правило

После успешного сброса пароля желательно:
 • отозвать все активные refresh token пользователя

Это повышает безопасность.

Для v1 это рекомендуется, а не строго обязательно.

⸻

1. Нефункциональные требования

⸻

NFR-1. Безопасность
 1. Пароль хранится только в hash-виде.
 2. Refresh token хранится только в hash-виде.
 3. Reset token хранится только в hash-виде.
 4. Ошибки логина не должны раскрывать, существует ли email.
 5. Время жизни access token должно быть коротким.
 6. Время жизни refresh token должно быть ограниченным.
 7. Время жизни reset token должно быть ограниченным.
 8. Все auth-события должны логироваться.

⸻

NFR-2. Читаемость кода

Код должен быть разделён по слоям:
 • API
 • service
 • repository
 • model/schema

Нельзя смешивать:
 • HTTP-логику
 • бизнес-логику
 • SQL-операции

⸻

NFR-3. Расширяемость

Реализация должна позволять позже добавить:
 • приглашения в семью
 • несколько admin
 • 2FA
 • email confirmation
 • список активных устройств
 • принудительный logout всех сессий

⸻

1. API-карта

⸻

POST /auth/register

Request

{
  "email": "<user@example.com>",
  "password": "StrongPassword123!",
  "family_name": "My Family"
}

Success response

{
  "message": "User registered successfully",
  "user_id": 1,
  "family_id": 1
}

Errors
 • 400 — неверные данные
 • 409 — email уже занят

⸻

POST /auth/login

Request

{
  "email": "<user@example.com>",
  "password": "StrongPassword123!"
}

Success response

{
  "access_token": "access_token_value",
  "refresh_token": "refresh_token_value",
  "token_type": "bearer"
}

Errors
 • 401 — неверные учётные данные
 • 403 — пользователь деактивирован

⸻

GET /auth/me

Request

Заголовок:

Authorization: Bearer <access_token>

Success response

{
  "id": 1,
  "email": "<user@example.com>",
  "role": "admin",
  "is_active": true,
  "family_id": 1,
  "created_at": "2026-03-28T18:00:00Z"
}

Errors
 • 401 — токен невалиден или истёк
 • 404 — пользователь не найден

⸻

POST /auth/refresh

Request

{
  "refresh_token": "refresh_token_value"
}

Success response

{
  "access_token": "new_access_token_value",
  "token_type": "bearer"
}

Errors
 • 401 — refresh token невалиден, истёк или отозван
 • 403 — пользователь неактивен

⸻

POST /auth/logout

Request

{
  "refresh_token": "refresh_token_value"
}

Success response

{
  "message": "Logged out successfully"
}

Errors

Для logout можно делать мягкое поведение:
 • даже если токен уже невалиден, возвращать нейтральный ответ

Это удобно для клиента.

⸻

POST /auth/password-reset/request

Request

{
  "email": "<user@example.com>"
}

Success response

{
  "message": "If the account exists, password reset instructions have been created"
}

⸻

POST /auth/password-reset/confirm

Request

{
  "token": "raw_reset_token",
  "new_password": "NewStrongPassword123!"
}

Success response

{
  "message": "Password updated successfully"
}

Errors
 • 400 — токен невалиден / истёк / использован
 • 400 — пароль не прошёл валидацию

⸻

1. Список backend-операций

Это то, что должен уметь backend внутри себя.

⸻

Операции над users
 • create_user
 • get_user_by_email
 • get_user_by_id
 • update_user_password
 • set_user_active_status

⸻

Операции над families
 • create_family
 • get_family_by_id
 • list_family_users

⸻

Операции над refresh_tokens
 • create_refresh_token
 • get_valid_refresh_token
 • revoke_refresh_token
 • revoke_all_user_refresh_tokens — желательно
 • list_user_refresh_tokens — на будущее

⸻

Операции над password_reset_tokens
 • create_password_reset_token
 • get_valid_password_reset_token
 • mark_password_reset_token_used
 • invalidate_user_reset_tokens

⸻

Операции над audit_logs
 • create_audit_log
 • list_user_audit_logs

⸻

1. Правила валидации

⸻

Email

Минимум:
 • непустой
 • корректный формат
 • приводить к единому виду, например lower-case

⸻

Пароль

Рекомендую зафиксировать минимум:
 • длина не менее 8 символов

Для v1 этого достаточно.
Позже можно усилить требования.

⸻

Family name

Минимум:
 • непустое
 • обрезать лишние пробелы по краям

⸻

1. Аудит-события

Минимальный список event_type:
 • register_success
 • login_success
 • login_failed
 • refresh_success
 • refresh_failed
 • logout
 • password_reset_requested
 • password_reset_completed
 • password_reset_failed

⸻

1. Критерии готовности этапа

Этап считается завершённым, если:
 1. пользователь может зарегистрироваться
 2. пользователь может войти
 3. access token работает на /auth/me
 4. refresh token выдаёт новый access token
 5. logout отзывает refresh token
 6. reset password request создаёт reset token
 7. reset password confirm меняет пароль
 8. все ключевые auth-события попадают в audit_logs
 9. неактивный пользователь не может войти
 10. повторное использование reset token невозможно

⸻

1. Порядок реализации

Чтобы не расползтись, пиши в таком порядке:

Шаг 1

Модели и доступ к БД:
 • users
 • families
 • refresh_tokens
 • password_reset_tokens
 • audit_logs

Шаг 2

Repository-слой:
 • create/get/update/revoke операции

Шаг 3

Service-слой:
 • register
 • login
 • refresh
 • logout
 • reset password

Шаг 4

API-слой:
 • endpoint’ы /auth/*

Шаг 5

Проверка сценариев руками:
 • register
 • login
 • me
 • refresh
 • logout
 • reset request
 • reset confirm

⸻

1. Что не делать при реализации
 • не смешивать SQL и HTTP в одном месте
 • не хранить raw token в БД
 • не хранить пароль в открытом виде
 • не писать всё в одном файле
 • не усложнять RBAC сейчас
 • не добавлять лишние поля без причины

⸻

Если хочешь, следующим сообщением я подготовлю тебе ещё более прикладной документ:
“план файлов и модулей для реализации этого ТЗ” — то есть что именно ты должен создать в models, repositories, services, api.
