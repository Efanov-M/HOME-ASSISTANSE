from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, TypeVar, ParamSpec

from sqlalchemy.orm import Session

from app.core.config import RESET_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.core.database import SessionLocal
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.models.family import Family
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.password_reset_repository import PasswordResetTokenRepository
from app.repositories.family_repository import FamilyRepository
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.core.security import (
    create_access_token,
    create_reset_token,
    create_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
    decode_access_token,
    validation_password
)
from app.core.errors import AuthError
from app.core.errors import (
    RefreshTokenNotFound,
    RefreshTokenRevoked,
    RefreshTokenExpired,
    RefreshTokenNoExpiry,
    RefreshUserBlocked,
    RefreshUserNotFound,
    AccessTokenNotFound,
    AccessUserBlocked,
    AccessUserNotFound,
    ResetTokenNotFound,
    ResetTokenUsed,
    ResetTokenNoExpiry,
    ResetTokenExpired
)

P = ParamSpec("P")
R = TypeVar("R")


def transactional(func: Callable[P, R]) -> Callable[P, R]:
    """EN: Wrap a service function in one database transaction.

    The decorator commits when the wrapped function succeeds
    and rolls back when any exception escapes.

    Args:
        func: Service function whose first positional argument is ``db``.

    Returns:
        Wrapped callable with transactional behavior.

    RU: Оборачивает сервисную функцию в одну транзакцию базы данных.

    Декоратор делает commit, если функция завершилась успешно,
    и rollback, если наружу вышло любое исключение.

    Аргументы:
        func: сервисная функция, у которой первый позиционный аргумент — это ``db``.

    Возвращает:
        Обёрнутую функцию с транзакционным поведением.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """EN: Execute the wrapped service function inside one transaction.

        RU: Выполняет обёрнутую сервисную функцию внутри одной транзакции.
        """

        db: Session = args[0]
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result

        except Exception:
            db.rollback()
            raise

    return wrapper

def write_audit_event_safely(
    user_id: int | None,
    event_type: str,
    ip_address: str | None,
    user_agent: str | None,
    details: dict[str, Any],
) -> None:
    """EN: Persist an audit event in an isolated session.

    This helper is intended for error-path logging, where we do not want
    the main business rollback to erase the audit trail.

    Args:
        user_id: Related user identifier or ``None``.
        event_type: Audit event type string.
        ip_address: Client IP address if available.
        user_agent: Client user-agent string if available.
        details: Additional JSON-serializable details.

    RU: Сохраняет audit-событие в отдельной независимой сессии.

    Этот helper предназначен для логирования error-path сценариев,
    когда мы не хотим, чтобы rollback основной бизнес-транзакции
    стёр запись из аудита.

    Аргументы:
        user_id: идентификатор связанного пользователя или ``None``.
        event_type: строка типа audit-события.
        ip_address: IP-адрес клиента, если он известен.
        user_agent: строка User-Agent клиента, если она известна.
        details: дополнительный JSON-совместимый контекст.
    """

    audit_db: Session = SessionLocal()
    try:
        audit_repository = AuditLogRepository(audit_db)
        audit_repository.create_audit_log(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        audit_db.commit()
    except Exception:
        audit_db.rollback()
    finally:
        audit_db.close()


def get_current_user(db: Session, token: str, ip_address: str) -> User:
    """EN: Resolve the current user from an access token.

    Args:
        db: Active database session.
        token: Raw access token string.
        ip_address: Client IP address for audit logging.

    Returns:
        Active authenticated ``User`` object.

    Raises:
        AuthError: If the token is invalid or the user is unavailable.

    RU: Возвращает текущего пользователя по access token.

    Аргументы:
        db: активная сессия базы данных.
        token: сырая строка access token.
        ip_address: IP-адрес клиента для записи в аудит.

    Возвращает:
        Активный аутентифицированный объект ``User``.

    Исключения:
        AuthError: Если токен невалиден или пользователь недоступен.
    """

    user_id = None

    try:
        # 1. decode JWT (любую ошибку приводим к AuthError)
        try:
            payload = decode_access_token(token)
        except Exception:
            raise AccessTokenNotFound()

        # 2. достаём user_id
        user_id = payload.get("user_id")
        if user_id is None:
            raise AccessTokenNotFound()

        # 3. проверяем пользователя
        user = validate_user_by_user_id(db, user_id)

        return user

    except AuthError as e:
        # OPTIMIZATION: error-path audit is written in a separate session
        # so the main transaction rollback does not erase the security log.
        write_audit_event_safely(
            user_id=user_id,
            event_type=e.event_type,
            ip_address=ip_address,
            user_agent=None,
            details={}
        )
        raise
    

def auth_required(func: Callable[P, R]) -> Callable[P, R]:
    """EN: Decorator that injects ``current_user`` after access-token validation.

    Args:
        func: Callable that expects ``db``, ``token``, and ``ip_address``.

    Returns:
        Wrapped callable with ``current_user`` injected into ``kwargs``.

    RU: Декоратор, который подставляет ``current_user`` после проверки access token.

    Аргументы:
        func: функция, ожидающая ``db``, ``token`` и ``ip_address``.

    Возвращает:
        Обёрнутую функцию, в ``kwargs`` которой добавляется ``current_user``.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """EN: Validate access context and inject ``current_user`` into kwargs.

        RU: Проверяет access-контекст и подставляет ``current_user`` в kwargs.
        """

        # 1. достаём обязательные аргументы
        db: Session = kwargs.get("db") or args[0]
        token: str | None = kwargs.get("token")
        ip_address: str | None = kwargs.get("ip_address")

        if token is None:
            raise AccessTokenNotFound()

        # 2. получаем пользователя (вся логика внутри get_current_user)
        user = get_current_user(db, token, ip_address)

        # 3. прокидываем user в функцию
        kwargs["current_user"] = user

        # 4. вызываем исходную функцию
        return func(*args, **kwargs)

    return wrapper


def validate_reset_token(db: Session, token_hash: str) -> PasswordResetToken:
    """EN: Validate a password reset token by its hash.

    Args:
        db: Active database session.
        token_hash: Hashed reset token value.

    Returns:
        Valid ``PasswordResetToken`` ORM object.

    Raises:
        AuthError: If the token does not exist, has no expiry, is expired, or was used.

    RU: Проверяет токен сброса пароля по его hash.

    Аргументы:
        db: активная сессия базы данных.
        token_hash: хеш reset token.

    Возвращает:
        Валидный ORM-объект ``PasswordResetToken``.

    Исключения:
        AuthError: Если токен не существует, не имеет срока действия, истёк или уже использован.
    """

    password_reset_repo = PasswordResetTokenRepository(db)
    
    token = password_reset_repo.get_password_reset_token_by_hash(token_hash)

    now = datetime.now(timezone.utc)
   
    
    if token is None:
        raise ResetTokenNotFound()
    
    if token.expires_at == None:
        raise ResetTokenNoExpiry()

    if now > token.expires_at:
        raise ResetTokenExpired()
    
    if token.used_at:
        raise ResetTokenUsed()
    
    return token

def validate_user_by_user_id(db: Session, user_id: int) -> User:
    """EN: Validate that a user exists and is active by user id.

    Args:
        db: Active database session.
        user_id: User identifier.

    Returns:
        Valid active ``User`` object.

    Raises:
        AuthError: If the user does not exist or is blocked.

    RU: Проверяет, что пользователь по id существует и активен.

    Аргументы:
        db: активная сессия базы данных.
        user_id: идентификатор пользователя.

    Возвращает:
        Валидный активный объект ``User``.

    Исключения:
        AuthError: Если пользователь не найден или заблокирован.
    """

    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if user is None:
        
        raise AccessUserNotFound()
    
    if not user.is_active:
       
        raise AccessUserBlocked()
    return user


def validate_user_by_email(db: Session, emai: str) -> User:
    """EN: Validate that a user exists and is active by email.

    Args:
        db: Active database session.
        emai: User email value.

    Returns:
        Valid active ``User`` object.

    Raises:
        AuthError: If the user does not exist or is blocked.

    RU: Проверяет, что пользователь по email существует и активен.

    Аргументы:
        db: активная сессия базы данных.
        emai: значение email пользователя.

    Возвращает:
        Валидный активный объект ``User``.

    Исключения:
        AuthError: Если пользователь не найден или заблокирован.
    """

    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(emai)
    if user is None:
        
        raise AccessUserNotFound()
    
    if not user.is_active:
       
        raise AccessUserBlocked()
    return user


def validate_refresh_token(
    db: Session,
    refresh_token: str,
    ip_address: str,
) -> tuple[RefreshToken, User]:
    """EN: Validate a refresh token and the user linked to it.

    Args:
        db: Active database session.
        refresh_token: Raw refresh token string from the client.
        ip_address: Client IP address kept for the surrounding auth flow.

    Returns:
        Tuple of ``(RefreshToken, User)``.

    Raises:
        AuthError: If the token is missing, revoked, expired, malformed,
            or linked to a missing/inactive user.

    RU: Проверяет refresh token и пользователя, которому он принадлежит.

    Аргументы:
        db: активная сессия базы данных.
        refresh_token: сырая строка refresh token от клиента.
        ip_address: IP-адрес клиента, сохраняемый для окружающего auth-сценария.

    Возвращает:
        Кортеж ``(RefreshToken, User)``.

    Исключения:
        AuthError: Если токен не найден, отозван, просрочен, повреждён
            или связан с отсутствующим/неактивным пользователем.
    """

    # подключаемся к бд
    refresh_repo = RefreshTokenRepository(db)
    user_repo = UserRepository(db)
   
    refresh_token_hash = hash_token(refresh_token)
    now = datetime.now(timezone.utc)
   
    token = refresh_repo.get_refresh_token_by_token_hash(refresh_token_hash)
    if token is None:
        
        raise RefreshTokenNotFound()
    
    if token.revoked_at:
        
        raise RefreshTokenRevoked()
    
    if token.expires_at == None:
        
        raise RefreshTokenNoExpiry()
    
    if now > token.expires_at:
        raise RefreshTokenExpired()
    
    user = user_repo.get_user_by_id(token.user_id)

    if user is None:
        
        raise RefreshUserNotFound()
    
    if not user.is_active:
       
        raise RefreshUserBlocked()
    
    return token, user
    
def validate_email(email: str) -> str:
    """EN: Validate and normalize an email address.

    The function trims whitespace, lowercases the value,
    and performs a small set of structural email checks.

    Args:
        email: Raw email string.

    Returns:
        Normalized email string.

    Raises:
        ValueError: If the email format is invalid.

    RU: Валидирует и нормализует email-адрес.

    Функция убирает внешние пробелы, переводит значение в нижний регистр
    и выполняет базовые структурные проверки email.

    Аргументы:
        email: сырой email в виде строки.

    Возвращает:
        Нормализованную строку email.

    Исключения:
        ValueError: Если формат email некорректен.
    """
    email = email.strip().lower()

    if not email:
        raise ValueError("Неверный формат email")

    if email.count("@") != 1:
        raise ValueError("Неверный формат email")

    local_part, domain_part = email.split("@")

    if not local_part or not domain_part:
        raise ValueError("Неверный формат email")

    if "." not in domain_part:
        raise ValueError("Неверный формат email")

    if domain_part.startswith(".") or domain_part.endswith("."):
        raise ValueError("Неверный формат email")

    return email

def validate_data(data: str) -> str:
    """EN: Normalize a generic text value and ensure it is not empty.

    Args:
        data: Raw string value received from input.

    Returns:
        Trimmed and lowercased string.

    Raises:
        ValueError: If the resulting value is empty.

    RU: Нормализует текстовое значение и проверяет, что оно не пустое.

    Аргументы:
        data: сырое строковое значение, пришедшее на вход.

    Возвращает:
        Строку без внешних пробелов и в нижнем регистре.

    Исключения:
        ValueError: Если после нормализации значение оказалось пустым.
    """

    data = data.strip().lower()
    if not data:
        raise ValueError ('Значение не должно быть пустым')
    return data 

@transactional
def register_family(db: Session, name: str) -> Family:
    """EN: Register a new family if a family with the same name does not exist.

    Args:
        db: Active database session.
        name: Family name to be created.

    Returns:
        Newly created ``Family`` ORM object.

    Raises:
        ValueError: If a family with the same name already exists.

    RU: Регистрирует новую семью, если семья с таким именем ещё не существует.

    Аргументы:
        db: активная сессия базы данных.
        name: имя семьи, которую нужно создать.

    Возвращает:
        Новый ORM-объект ``Family``.

    Исключения:
        ValueError: Если семья с таким именем уже существует.
    """

    family_repository = FamilyRepository(db)

    existing_family = family_repository.get_family_by_name(name)

    if existing_family is not None:
        raise ValueError("Семья с таким именем уже существует")

    new_family = family_repository.create_family(name)

    return new_family
        
@transactional
def register_user(db: Session, email: str, password: str, family_name: str) -> User:
    """EN: Register a user and either join or create a family.

    The function validates input, checks email uniqueness,
    decides whether the family already exists,
    and assigns ``admin`` or ``user`` role accordingly.

    Args:
        db: Active database session.
        email: Raw user email.
        password: Raw user password before hashing.
        family_name: Name of the family to join or create.

    Returns:
        Newly created ``User`` ORM object.

    Raises:
        ValueError: If the email is already used or validation fails.

    RU: Регистрирует пользователя и либо присоединяет его к семье, либо создаёт новую.

    Функция валидирует входные данные, проверяет уникальность email,
    определяет, существует ли уже семья,
    и в зависимости от этого назначает роль ``admin`` или ``user``.

    Аргументы:
        db: активная сессия базы данных.
        email: сырой email пользователя.
        password: сырой пароль пользователя до хеширования.
        family_name: имя семьи, к которой нужно присоединиться или которую нужно создать.

    Возвращает:
        Новый ORM-объект ``User``.

    Исключения:
        ValueError: Если email уже занят или входные данные не проходят проверку.
    """

    family_repository = FamilyRepository(db)
    user_repository = UserRepository(db)
    # Проверяем email на валидацию
    email = validate_email(email)
    family_name = validate_data(family_name)
    # проверяем есть ли пользователь в системе 
    existing_user = user_repository.get_user_by_email(email)
    if existing_user is not None:
        raise ValueError("Пользователь с таким email уже существует")
    
    password_hash = get_password_hash(password) # функция из будущего
    # проверяем есть ли семья с данным name. Если есть то пользователь создается 
    # с ролью user, если нет то admin
    existing_family = family_repository.get_family_by_name(family_name)
    if existing_family is None:
        new_family = family_repository.create_family(family_name)
        family_id = new_family.id
        role = UserRole.admin
    else:
        role = UserRole.user
        family_id = existing_family.id
    new_user = user_repository.create_user(email, password_hash, role, family_id) 
    
    return new_user

@transactional
def login_user(
    db: Session,
    email: str,
    password: str,
    ip_address: str,
    user_agent: str,
) -> dict[str, str]:
    """EN: Authenticate a user, create tokens, and write audit events.

    Args:
        db: Active database session.
        email: Email used for login.
        password: Raw password to verify.
        ip_address: Client IP address for audit and token storage.
        user_agent: Client user-agent string for audit and token storage.

    Returns:
        Dictionary containing ``access_token`` and ``refresh_token``.

    Raises:
        ValueError: If the user is missing, blocked, or provides a wrong password.

    RU: Аутентифицирует пользователя, создаёт токены и пишет события в аудит.

    Аргументы:
        db: активная сессия базы данных.
        email: email для входа в систему.
        password: сырой пароль для проверки.
        ip_address: IP-адрес клиента для аудита и хранения токена.
        user_agent: строка User-Agent клиента для аудита и хранения токена.

    Возвращает:
        Словарь с ключами ``access_token`` и ``refresh_token``.

    Исключения:
        ValueError: Если пользователь не найден, заблокирован или ввёл неверный пароль.
    """

   # 2. инициализируем репозитории
    user_repository = UserRepository(db)
    audit_repository = AuditLogRepository(db)
    refresh_token_repository = RefreshTokenRepository(db)

    #   3. ищем пользователя
    existing_user = user_repository.get_user_by_email(email)

    # 4. если пользователь не найден — логируем и падаем
    if existing_user is None:
        # OPTIMIZATION: failed-login audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id=None,
            event_type="login_failed_user_not_found",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": email}
        )
        raise ValueError("Пользователь с таким email не существует")

    # 5. проверяем активность
    if not existing_user.is_active:
        # OPTIMIZATION: failed-login audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id=existing_user.id,
            event_type="login_failed_user_blocked",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": email}
        )
        raise ValueError("Пользователь заблокирован")

    # 6. проверяем пароль
    if not verify_password(password, existing_user.password_hash):
        # OPTIMIZATION: failed-login audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id=existing_user.id,
            event_type="login_failed_wrong_password",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": email}
        )
        raise ValueError("Неверный пароль")

    # 7. создаём access token (JWT)
    access_token = create_access_token(existing_user.id, existing_user.role)

    # 8. создаём refresh token (raw строка)
    refresh_token = create_refresh_token()

    # 9. делаем hash refresh token (для БД)
    refresh_token_hash = hash_token(refresh_token)

    # 10. считаем срок жизни refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # 11. сохраняем refresh token (в виде hash) в БД
    refresh_token_repository.create_refresh_token(
        existing_user.id,
        refresh_token_hash,
        expires_at,
        ip_address,
        user_agent
    )
    
    # 12. логируем успешный вход
    audit_repository.create_audit_log(
        user_id=existing_user.id,
        event_type="login_success",
        ip_address=ip_address,
        user_agent=user_agent,
        details={"email": email}
    )

    # 13. возвращаем токены клиенту
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@transactional
def refresh_access_token(db: Session, refresh_token: str, ip_address: str) -> str:
    """EN: Validate a refresh token and return a new access token.

    Args:
        db: Active database session.
        refresh_token: Raw refresh token string.
        ip_address: Client IP address used for audit logging.

    Returns:
        Newly created access token string.

    Raises:
        AuthError: If refresh-token validation fails.

    RU: Проверяет refresh token и возвращает новый access token.

    Аргументы:
        db: активная сессия базы данных.
        refresh_token: сырая строка refresh token.
        ip_address: IP-адрес клиента для записи в аудит.

    Возвращает:
        Новый access token в виде строки.

    Исключения:
        AuthError: Если проверка refresh token завершается ошибкой.
    """

    audit_repository = AuditLogRepository(db)
    token = None
    user = None

    try:
        token, user = validate_refresh_token(db, refresh_token, ip_address)

    except AuthError as e:
        # OPTIMIZATION: error-path audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id=token.user_id if token else None,
            event_type=e.event_type,
            ip_address=ip_address,
            user_agent=token.user_agent if token else None,
            details={}
        )
        raise
    
    access_token = create_access_token(user.id, user.role)
    audit_repository.create_audit_log(
            user_id=user.id,
            event_type="refresh_success",
            ip_address=ip_address,
            user_agent=token.user_agent,
            details={"email": user.email}
        )
    
    return access_token


@transactional
def logout_user(db: Session, refresh_token: str, ip_address: str) -> bool:
    """EN: Revoke a refresh token and write a logout audit event.

    Args:
        db: Active database session.
        refresh_token: Raw refresh token string.
        ip_address: Client IP address used for audit logging.

    Returns:
        ``True`` when logout completes successfully.

    Raises:
        AuthError: If refresh-token validation fails.

    RU: Отзывает refresh token и пишет audit-событие logout.

    Аргументы:
        db: активная сессия базы данных.
        refresh_token: сырая строка refresh token.
        ip_address: IP-адрес клиента для записи в аудит.

    Возвращает:
        ``True``, если logout завершён успешно.

    Исключения:
        AuthError: Если проверка refresh token завершается ошибкой.
    """

    refresh_repo = RefreshTokenRepository(db)
    audit_repository = AuditLogRepository(db)

    token = None
    user = None

    try:
        token, user = validate_refresh_token(db, refresh_token, ip_address)

    except AuthError as e:
        # OPTIMIZATION: error-path audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id=token.user_id if token else None,
            event_type=e.event_type,
            ip_address=ip_address,
            user_agent=token.user_agent if token else None,
            details={}
        )
        raise

    # revoke
    refresh_repo.revoke_refresh_token(token)

    # audit success
    audit_repository.create_audit_log(
        user_id=user.id,
        event_type="logout_success",
        ip_address=ip_address,
        user_agent=token.user_agent,
        details={"email": user.email}
    )

    return True

@transactional
def request_password_reset(
    db: Session,
    email: str,
    ip_address: str,
    user_agent: str,
) -> str:
    """EN: Create a password reset token request flow with neutral external response.

    Args:
        db: Active database session.
        email: Email for which reset is requested.
        ip_address: Client IP address for audit logging.
        user_agent: Client user-agent string for audit logging.

    Returns:
        Neutral human-readable message.

    RU: Запускает сценарий запроса на сброс пароля с нейтральным внешним ответом.

    Аргументы:
        db: активная сессия базы данных.
        email: email, для которого запрашивается сброс.
        ip_address: IP-адрес клиента для записи в аудит.
        user_agent: строка User-Agent клиента для записи в аудит.

    Возвращает:
        Нейтральное текстовое сообщение для внешнего ответа.
    """

    password_reset_repo = PasswordResetTokenRepository(db)
    audit_repository = AuditLogRepository(db)
    email = validate_email(email)
    
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)

    if user is None:
        # OPTIMIZATION: error/neutral-path audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id = None,
            event_type = 'password_reset_requested',
            ip_address = ip_address,
            user_agent = user_agent,
            details = {'email': email}
        )
        return 'If the account exists, password reset instructions have been sent\nЕсли пользователь существует, инструкции по восстановлению отправлены'
    
    
    reset_token = create_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
   
    refresh_token_hash = hash_token(reset_token)
    # сохраняем refresh token (в виде hash) в БД
    password_reset_repo.create_password_reset_token(
        user.id,
        refresh_token_hash,
        expires_at,
    )
    audit_repository.create_audit_log(
            user_id = user.id,
            event_type = 'password_reset_token_created' ,
            ip_address = ip_address,
            user_agent = user_agent,
            details = {'email': email}
        )
    return 'If the account exists, password reset instructions have been sent\nЕсли пользователь существует, инструкции по восстановлению отправлены'

@transactional
def confirm_password_reset(
    db: Session,
    reset_token: str,
    ip_address: str,
    password: str,
) -> str:
    """EN: Confirm password reset using a valid reset token and a new password.

    Args:
        db: Active database session.
        reset_token: Raw reset token string from the client.
        ip_address: Client IP address for audit logging.
        password: New raw password value.

    Returns:
        Success message string.

    Raises:
        AuthError: If the reset token is invalid.
        ValueError: If the new password does not satisfy password policy.

    RU: Подтверждает сброс пароля по валидному reset token и новому паролю.

    Аргументы:
        db: активная сессия базы данных.
        reset_token: сырая строка reset token от клиента.
        ip_address: IP-адрес клиента для записи в аудит.
        password: новое сырое значение пароля.

    Возвращает:
        Строку с сообщением об успешном обновлении.

    Исключения:
        AuthError: Если reset token невалиден.
        ValueError: Если новый пароль не проходит парольную политику.
    """

# Должно работать
#  • принять raw reset token
#  • сделать hash
#  • найти запись
#  • проверить:
#  • токен существует
#  • токен не просрочен
#  • токен ещё не использован
#  • провалидировать новый пароль
#  • захешировать новый пароль
#  • обновить пароль пользователя
#  • пометить reset token использованным
#  • записать audit log
#  • вернуть message response
    audit_repository = AuditLogRepository(db)
    reset_token_hash = hash_token(reset_token)
    token = None
    try:
        token = validate_reset_token(db, reset_token_hash)

    except AuthError as e:
        # OPTIMIZATION: error-path audit is written through a separate session
        # so rollback of the main flow does not delete the security event.
        write_audit_event_safely(
            user_id = token.user_id if token else None,
            event_type = e.event_type,
            ip_address = ip_address,
            user_agent =  None,
            details = {}
        )
        raise

    passwd = validation_password(password)
    passwd_hash = get_password_hash(passwd)
    
    user_repo = UserRepository(db)
    user_repo.update_user_password(token.user_id,passwd_hash)
    reset_repo = PasswordResetTokenRepository(db)
    reset_repo.mark_token_as_used(reset_token_hash)

    audit_repository.create_audit_log(
            user_id = token.user_id,
            event_type = "password_reset_confirmed",
            ip_address = ip_address,
            user_agent =  None,
            details = {}
        )
    return 'Пароль успешно обновлён'
 
