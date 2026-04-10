
ТЗ 2 — Auth Core MVP для проекта Home Secretary

1. Смысл этапа

На этом этапе мы не создаём проект с нуля.
Мы берём уже существующий фундамент и доводим auth-ядро до рабочего состояния.

То есть задача этапа:

собрать минимально законченный backend-блок аутентификации и пользователей, который уже можно будет запускать через FastAPI и тестировать как реальный сервис.

⸻

1. Что уже считается сделанным

Это важно, чтобы не делать лишнюю работу повторно.

У тебя уже есть:
 • структура проекта
 • database.py
 • ORM-модели
 • repository-слой
 • базовый security.py
 • частично собранный auth_service.py
 • Docker + PostgreSQL
 • SQL init для БД

Значит на этом этапе не нужно снова возвращаться к проектированию схемы.
Схема уже есть. Теперь задача — довести поведение системы.

⸻

1. Главная цель этапа

После завершения ТЗ 2 должна работать такая цепочка:
 • регистрация пользователя
 • вход в систему
 • выдача access token и refresh token
 • обновление access token через refresh token
 • выход из системы
 • получение текущего пользователя через access token
 • запрос на сброс пароля
 • подтверждение сброса пароля

И всё это должно работать через:
 • FastAPI endpoint’ы
 • service-слой
 • repository-слой
 • PostgreSQL

⸻

1. Что входит в ТЗ 2

Входит:
 • доведение config.py
 • доведение database.py
 • доведение security.py
 • доведение repository под auth use case
 • доведение auth_service.py
 • создание schemas/
 • создание api/auth.py
 • создание main.py
 • подключение FastAPI к БД через dependency
 • ручная проверка auth-сценариев

⸻

1. Что в ТЗ 2 не входит

Чтобы не расползтись в стороны, этот этап не включает:
 • frontend
 • email-отправку
 • 2FA
 • rate limiting
 • Alembic
 • HTTPS / reverse proxy
 • календарь
 • todo
 • финансы
 • документы
 • Matrix
 • политику сложных прав доступа сверх admin/user

То есть сейчас только:

Auth + Users + Families backend core

⸻

1. Архитектурное правило этапа

Всё, что ты будешь делать дальше, должно укладываться в такую цепочку:

API -> Service -> Repository -> DB

Где:
 • API принимает HTTP-запрос
 • Service решает сценарий
 • Repository работает с таблицами
 • DB хранит данные

Запрещено смешивать это между собой.

⸻

1. Подзадачи этапа

Теперь главное. Я разобью ТЗ на реальные рабочие блоки.

⸻

Блок A. Конфигурация и подключение к БД

Цель блока

Сделать так, чтобы приложение получало настройки из одного места и стабильно работало с БД.

Нужно сделать

A.1. Довести config.py
В config.py должны храниться и читаться из env следующие значения:
 • SECRET_KEY
 • DATABASE_URL
 • ACCESS_TOKEN_EXPIRE_MINUTES
 • REFRESH_TOKEN_EXPIRE_DAYS

Требование

Если обязательная переменная отсутствует, приложение должно падать сразу и понятно.

⸻

A.2. Довести database.py
В database.py должно быть:
 • подключение через DATABASE_URL из config.py
 • engine
 • SessionLocal
 • Base
 • get_db()

Требование

Никакого хардкода строки подключения в database.py после завершения этого блока быть не должно.

⸻

Критерий готовности блока A
Блок считается готовым, если:
 • config.py читает все критичные переменные
 • database.py использует config.py
 • есть get_db()
 • можно получить рабочую SQLAlchemy Session через dependency

⸻

Блок B. Security слой

Цель блока

Зафиксировать единый и понятный security API.

В security.py должны быть рабочие функции:
 • validation_password
 • get_password_hash
 • verify_password
 • create_access_token
 • create_refresh_token
 • hash_token

Дополнительно нужно добавить:
 • decode_access_token

Требования
 • SECRET_KEY берётся из config
 • TTL access token берётся из config
 • TTL refresh token берётся из config или контролируется на service-уровне, но без магических чисел по всему коду
 • refresh token должен быть достаточно длинным и случайным
 • hash_token должен использовать криптографический хеш

⸻

Критерий готовности блока B
Блок готов, если:
 • пароль валидируется
 • пароль хешируется
 • пароль проверяется
 • access token создаётся и декодируется
 • refresh token создаётся
 • refresh token можно безопасно хешировать

⸻

Блок C. Repository слой под auth use case

Цель блока

Сделать repository не “вообще”, а под конкретные auth-сценарии.

Нужно проверить и довести:

C.1. UserRepository
Должны быть методы:
 • get_user_by_email
 • get_user_by_id
 • create_user
 • update_user_password

Опционально позже:
 • set_user_active_status

⸻

C.2. FamilyRepository
Должны быть методы:
 • get_family_by_name
 • create_family

Вопрос created_by пока не усложняем, но поле должно быть согласовано с моделью и схемой.

⸻

C.3. RefreshTokenRepository
Должны быть методы:
 • get_refresh_token_by_token_hash
 • create_refresh_token
 • revoke_refresh_token

⸻

C.4. PasswordResetTokenRepository
Должны быть методы:
 • create_password_reset_token
 • get_password_reset_token_by_hash
 • mark_token_as_used

⸻

C.5. AuditLogRepository
Должны быть методы:
 • create_audit_log
 • get_audit_logs_by_user_id

⸻

Требование ко всем repository
Repository не должны:
 • создавать токены
 • решать бизнес-логику
 • валидировать пароль
 • декодировать JWT

Repository только работают с БД.

⸻

Блок D. Auth service

Это главный блок ТЗ 2.

Цель блока

Собрать законченные auth-сценарии.

⸻

D.1. register_user

Должно работать
 • валидация email
 • валидация family_name
 • проверка, что email ещё не занят
 • хеширование пароля
 • поиск или создание семьи
 • назначение роли:
 • admin если семья создаётся впервые
 • user если семья уже есть
 • создание пользователя
 • audit log

Результат

Возвращается созданный пользователь или структура для API.

⸻

D.2. login_user

Должно работать
 • нормализация email
 • поиск пользователя
 • проверка, что пользователь существует
 • проверка is_active
 • проверка пароля
 • создание access token
 • создание refresh token
 • хеширование refresh token
 • сохранение hash refresh token в БД
 • запись audit log
 • возврат:
 • access_token
 • refresh_token

⸻

D.3. refresh_access_token

Должно работать
 • принять raw refresh token
 • сделать hash
 • найти запись по hash
 • проверить:
 • токен существует
 • токен не просрочен
 • токен не отозван
 • найти пользователя
 • проверить is_active
 • создать новый access token
 • записать audit log
 • вернуть новый access token

⸻

D.4. logout_user

Должно работать
 • принять raw refresh token
 • сделать hash
 • найти запись
 • если токен не найден — audit + ошибка
 • если пользователь не найден — audit + ошибка
 • вызвать revoke_refresh_token
 • записать audit log
 • вернуть результат завершения logout

⸻

D.5. get_current_user

Это новый обязательный сценарий
Должно работать так:
 • принять access token
 • декодировать его
 • достать user_id
 • найти пользователя в БД
 • проверить, что пользователь существует
 • вернуть текущего пользователя

Это сервисная основа для /auth/me.

⸻

D.6. request_password_reset

Должно работать
 • принять email
 • найти пользователя
 • если пользователь не найден — вернуть нейтральный ответ, без раскрытия факта существования пользователя
 • создать raw reset token
 • сделать hash reset token
 • сохранить hash в БД
 • записать audit log
 • вернуть нейтральный response

На этом этапе не отправляем email.
Пока только готовим backend flow.

⸻

D.7. confirm_password_reset

Должно работать
 • принять raw reset token
 • сделать hash
 • найти запись
 • проверить:
 • токен существует
 • токен не просрочен
 • токен ещё не использован
 • провалидировать новый пароль
 • захешировать новый пароль
 • обновить пароль пользователя
 • пометить reset token использованным
 • записать audit log
 • вернуть message response

⸻

Требования ко всему auth_service.py

Нужно убрать:
 • лишние импорты
 • неиспользуемые модели в service
 • ошибки в event_type
 • ошибки с res.id вместо user_id
 • ошибки с обращением к полям, которых нет у модели
 • самопересекающиеся зависимости

⸻

Критерий готовности блока D
Блок готов, если все 7 сценариев выше логически завершены и не противоречат архитектуре.

⸻

Блок E. Schemas

Цель блока

Сделать чёткий контракт между API и backend-логикой.

Нужно создать:

schemas/auth.py
Минимум:
 • RegisterRequest
 • LoginRequest
 • RefreshRequest
 • LogoutRequest
 • PasswordResetRequest
 • PasswordResetConfirmRequest
 • TokenResponse
 • MessageResponse

⸻

schemas/user.py
Минимум:
 • UserResponse
 • MeResponse

⸻

schemas/family.py
Минимум:
 • FamilyResponse

⸻

Требование

Схемы должны описывать:
 • входные данные endpoint
 • выходные данные endpoint

И не должны содержать бизнес-логику.

⸻

Блок F. API слой

Цель блока

Поднять HTTP API над service-слоем.

Нужно создать api/auth.py

В нём должны быть endpoint’ы:
 • POST /auth/register
 • POST /auth/login
 • POST /auth/refresh
 • POST /auth/logout
 • GET /auth/me
 • POST /auth/password-reset/request
 • POST /auth/password-reset/confirm

⸻

Правило API слоя

API слой:
 • принимает request schema
 • получает db через get_db
 • вызывает service
 • возвращает response schema

В API запрещено:
 • писать SQLAlchemy query
 • хешировать пароль
 • делать JWT руками
 • писать бизнес-логику

⸻

Блок G. main.py

Цель блока

Сделать запускаемую точку входа приложения.

Нужно

Создать main.py, в котором:
 • создаётся FastAPI()
 • подключается auth router
 • опционально создаётся health endpoint

⸻

Блок H. requirements.txt

Цель блока

Сделать файл зависимостей пригодным для установки.

Сейчас проблема

У тебя в requirements.txt написаны команды pip install ..., а не сами пакеты.

Нужно

Сделать обычный список зависимостей, без pip install.

Минимально там должны быть зависимости для:
 • FastAPI
 • SQLAlchemy
 • psycopg
 • pwdlib
 • pyjwt
 • python-dotenv
 • pydantic
 • uvicorn

⸻

1. Критерии готовности ТЗ 2

ТЗ 2 считается закрытым, если выполняется всё ниже:

 1. config.py хранит ключевые настройки
 2. database.py использует config и выдаёт session
 3. регистрация работает
 4. логин работает
 5. refresh работает
 6. logout работает
 7. /auth/me работает
 8. password reset request работает
 9. password reset confirm работает
 10. audit logs пишутся на все auth-сценарии
 11. есть schemas
 12. есть api/auth.py
 13. есть main.py
 14. requirements.txt можно использовать для установки
 15. весь код укладывается в архитектуру:

 • API -> Service -> Repository -> DB

⸻

1. Порядок выполнения для тебя

С учётом твоего уровня правильный порядок такой:

Шаг 1

Довести:
 • config.py
 • database.py
 • requirements.txt

Шаг 2

Довести:
 • security.py

Шаг 3

Довести:
 • repositories под missing methods

Шаг 4

Довести:
 • auth_service.py
 • register
 • login
 • refresh
 • logout
 • get_current_user
 • reset flows

Шаг 5

Создать:
 • schemas/*

Шаг 6

Создать:
 • api/auth.py

Шаг 7

Создать:
 • main.py

Шаг 8

Прогнать сценарии руками

⸻

1. Что я считаю самым важным

На этом этапе твоя задача — не “написать побольше кода”.
Твоя задача — научиться собирать законченную backend-фичу по слоям.

Если ты закроешь это ТЗ, у тебя уже будет не абстрактное обучение, а реальный auth-модуль уровня MVP.

⸻

1. Мой короткий итог

Это и есть моё готовое ТЗ 2, адаптированное под твой проект и твой уровень:

довести существующий auth/users/families backend до рабочего FastAPI MVP, не переписывая всё заново, а аккуратно завершая уже созданные слои и добавляя недостающие сценарии.

⸻

Дальше правильно не обсуждать всё сразу, а взять только первый подшаг ТЗ 2.
И он у нас уже определён:

Шаг 1: довести config.py, database.py, requirements.txt.
