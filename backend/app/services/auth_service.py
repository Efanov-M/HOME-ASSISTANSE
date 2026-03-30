from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.models.user import User, UserRole
from app.models.family import Family
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.family_repository import FamilyRepository
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.auth_service import create_access_token, create_refresh_token, hash_token, verify_password, get_password_hash




def validate_email(email: str) -> str:
    """
    Validate and normalize an email address.

    The function:
    1. strips leading and trailing whitespace,
    2. converts the email to lowercase,
    3. checks that there is exactly one '@',
    4. checks that local and domain parts are not empty,
    5. checks that the domain contains a dot,
    6. checks that the domain does not start or end with a dot.

    Args:
        email: Raw email string.

    Returns:
        Normalized email string.

    Raises:
        ValueError: If the email format is invalid.
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

def validate_data(data:str):
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

def register_family(db, name: str):
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
        

def register_user(db, email: str, password: str, family_name: str ):
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




def login_user(db, email: str,password: str, ip_address: str, user_agent: str):
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
        audit_repository.create_audit_log(
            user_id=None,
            event_type="login_failed_user_not_found",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": email}
        )
        raise ValueError("Пользователь с таким email не существует")

    # 5. проверяем активность
    if not existing_user.is_active:
        audit_repository.create_audit_log(
            user_id=existing_user.id,
            event_type="login_failed_user_blocked",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": email}
    )
        raise ValueError("Пользователь заблокирован")

    # 6. проверяем пароль
    if not verify_password(password, existing_user.password_hash):
        audit_repository.create_audit_log(
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
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

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


def refresh_access_token(db, refresh_token):
    """EN: Validate a refresh token and issue a new access token.

    Args:
        db: Active database session.
        refresh_token: Raw refresh token received from the client.

    Returns:
        Newly created access token string.

    Raises:
        ValueError: If the refresh token is missing, expired, revoked,
            or belongs to an inactive user.

    RU: Проверяет refresh token и выпускает новый access token.

    Аргументы:
        db: активная сессия базы данных.
        refresh_token: сырой refresh token, полученный от клиента.

    Возвращает:
        Новый access token в виде строки.

    Исключения:
        ValueError: Если refresh token не найден, истёк, отозван
            или принадлежит неактивному пользователю.
    """

    # подключаемся к бд
    audit_repository = AuditLogRepository(db)
    refresh_token_db = RefreshTokenRepository(db)
    user_repository = UserRepository(db)

    # получаем хэш токена
    refresh_token_hash = hash_token(refresh_token)
    # по хэшу смотрим наличии записи в бд
    res = refresh_token_db.get_refresh_token_by_token_hash(refresh_token_hash)
    # если записи нет то ошибка
    if not res:
        audit_repository.create_audit_log(
            user_id=None,
            event_type="refresh_failed_token_not_found",
            ip_address=None,
            user_agent=None,
            details={"email": None}
        )

        raise ValueError ('Токен не существует')
    # запись есть, получаем пользователя для ведения логов
    user = user_repository.get_user_by_id(res.user_id)
    user_id = user.id
    email = user.email
    ip = res.ip_address
    us_agent = res.user_agent
    # проверяем истек ли срок у токена или нет 
    if datetime.now(timezone.utc) > res.expires_at:
        audit_repository.create_audit_log(
            user_id=user_id,
            event_type="refresh_failed_token_expired",
            ip_address=ip,
            user_agent=us_agent,
            details={"email": email}
        )
        raise ValueError ("У токена истек срок действия")
    # проверяем не был ли отозван токкен
    if res.revoked_at is not None:
        audit_repository.create_audit_log(
            user_id=res.id,
            event_type="refresh_failed_token_revoked",
            ip_address=res.ip_address,
            user_agent=res.user_agent,
            details={"email": res.email}
        )
        raise ValueError (" Токен был отозван ")
    #
    if not user.is_active:
        audit_repository.create_audit_log(
            user_id=res.id,
            event_type="refresh_failed_user_blocked",
            ip_address=res.ip_address,
            user_agent=res.user_agent,
            details={"email": res.email}
        )
        raise ValueError (" Пользователь не активен ")
    
    access_token = create_access_token(user_id, user.role)
    audit_repository.create_audit_log(
            user_id=res.id,
            event_type="refresh_failed_user_blocked",
            ip_address=res.ip_address,
            user_agent=res.user_agent,
            details={"email": res.email}
        )

    return access_token


    

        
