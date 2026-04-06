class AuthError(Exception):
    """
    EN: Base authentication error.

    This class is used as a parent for all auth-related exceptions.
    It contains a unified structure:
    - message (human readable)
    - event_type (for audit logs)

    RU: Базовая ошибка аутентификации.

    Используется как родитель для всех ошибок, связанных с авторизацией.
    Содержит:
    - message (человекочитаемое сообщение)
    - event_type (для audit логов)
    """

    def __init__(self, message: str, event_type: str):
        """EN: Initialize a structured authentication error.

        Args:
            message: Human-readable error message.
            event_type: Audit-friendly event type string.

        RU: Инициализирует структурированную ошибку аутентификации.

        Аргументы:
            message: человекочитаемое сообщение об ошибке.
            event_type: строка типа события для аудита.
        """

        self.message = message
        self.event_type = event_type
        super().__init__(message)


# ===== TOKEN ERRORS =====

class RefreshTokenNotFound(AuthError):
    """EN: Error raised when a refresh token record cannot be found.

    RU: Ошибка, которая выбрасывается, когда запись refresh token не найдена.
    """

    def __init__(self) -> None:
        """EN: Create an error for a missing refresh token.

        RU: Создаёт ошибку для отсутствующего refresh token.
        """

        super().__init__(
            message="Токен не существует",
            event_type="refresh_token_not_found"
        )


class RefreshTokenRevoked(AuthError):
    """EN: Error raised when a refresh token was already revoked.

    RU: Ошибка, которая выбрасывается, когда refresh token уже был отозван.
    """

    def __init__(self) -> None:
        """EN: Create an error for an already revoked refresh token.

        RU: Создаёт ошибку для уже отозванного refresh token.
        """

        super().__init__(
            message="Токен уже отозван",
            event_type="refresh_token_revoked"
        )


class RefreshTokenExpired(AuthError):
    """EN: Error raised when a refresh token is already expired.

    RU: Ошибка, которая выбрасывается, когда срок действия refresh token уже истёк.
    """

    def __init__(self) -> None:
        """EN: Create an error for an expired refresh token.

        RU: Создаёт ошибку для просроченного refresh token.
        """

        super().__init__(
            message="Токен истёк",
            event_type="refresh_token_expired"
        )


class RefreshTokenNoExpiry(AuthError):
    """EN: Error raised when a refresh token has no expiration timestamp.

    RU: Ошибка, которая выбрасывается, когда у refresh token нет срока действия.
    """

    def __init__(self) -> None:
        """EN: Create an error for a refresh token without expiry information.

        RU: Создаёт ошибку для refresh token без информации о сроке действия.
        """

        super().__init__(
            message="Срок действия токена не определён",
            event_type="refresh_token_no_expiry"
        )


# ===== USER ERRORS =====

class RefreshUserNotFound(AuthError):
    """EN: Error raised when refresh flow points to a missing user.

    RU: Ошибка, которая выбрасывается, когда refresh-сценарий ссылается на отсутствующего пользователя.
    """

    def __init__(self) -> None:
        """EN: Create an error for a missing user during refresh flow.

        RU: Создаёт ошибку для отсутствующего пользователя в refresh-сценарии.
        """

        super().__init__(
            message="Пользователь не существует",
            event_type="refresh_user_not_found"
        )


class RefreshUserBlocked(AuthError):
    """EN: Error raised when refresh flow points to a blocked user.

    RU: Ошибка, которая выбрасывается, когда refresh-сценарий ссылается на заблокированного пользователя.
    """

    def __init__(self) -> None:
        """EN: Create an error for a blocked user during refresh flow.

        RU: Создаёт ошибку для заблокированного пользователя в refresh-сценарии.
        """

        super().__init__(
            message="Пользователь не активен",
            event_type="refresh_user_blocked"
        )

class AccessUserNotFound(AuthError):
    """EN: Error raised when access-token flow cannot find the user.

    RU: Ошибка, которая выбрасывается, когда в access-сценарии не найден пользователь.
    """

    def __init__(self) -> None:
        """EN: Create an error for a missing user during access-token flow.

        RU: Создаёт ошибку для отсутствующего пользователя в access-сценарии.
        """

        super().__init__(
            message="Пользователь не существует",
            event_type="access_user_not_found"
        )


class AccessUserBlocked(AuthError):
    """EN: Error raised when access-token flow resolves to a blocked user.

    RU: Ошибка, которая выбрасывается, когда access-сценарий приводит к заблокированному пользователю.
    """

    def __init__(self) -> None:
        """EN: Create an error for a blocked user during access-token flow.

        RU: Создаёт ошибку для заблокированного пользователя в access-сценарии.
        """

        super().__init__(
            message="Пользователь не активен",
            event_type="access_user_blocked"
        )


# ====== ACCESS ERRORS ========

class AccessTokenNotFound(AuthError):
    """EN: Error raised when an access token is missing or cannot be used.

    RU: Ошибка, которая выбрасывается, когда access token отсутствует или непригоден к использованию.
    """

    def __init__(self) -> None:
        """EN: Create an error for a missing or invalid access token.

        RU: Создаёт ошибку для отсутствующего или невалидного access token.
        """

        super().__init__(
            message="Токен не существует",
            event_type="access_refresh_token_not_found"
        )



# ====== RESET TOKEN ERRORS ==========

class ResetTokenNotFound(AuthError):
    """EN: Error raised when a password reset token cannot be found.

    RU: Ошибка, которая выбрасывается, когда токен сброса пароля не найден.
    """

    def __init__(self) -> None:
        """EN: Create an error for a missing password reset token.

        RU: Создаёт ошибку для отсутствующего reset token.
        """

        super().__init__(
            message="Токен не существует",
            event_type="reset_token_not_found"
        )

class ResetTokenUsed(AuthError):
    """EN: Error raised when a password reset token was already used.

    RU: Ошибка, которая выбрасывается, когда токен сброса пароля уже был использован.
    """

    def __init__(self) -> None:
        """EN: Create an error for an already used password reset token.

        RU: Создаёт ошибку для уже использованного reset token.
        """

        super().__init__(
            message="Токен был использован",
            event_type="reset_token_was_used"
        )

class ResetTokenNoExpiry(AuthError):
    """EN: Error raised when a reset token has no expiration timestamp.

    RU: Ошибка, которая выбрасывается, когда у reset token нет срока действия.
    """

    def __init__(self) -> None:
        """EN: Create an error for a reset token without expiry information.

        RU: Создаёт ошибку для reset token без информации о сроке действия.
        """

        super().__init__(
            message="Срок действия токена не определён",
            event_type="reset_token_no_expiry"
        )

class ResetTokenExpired(AuthError):
    """EN: Error raised when a password reset token is expired.

    RU: Ошибка, которая выбрасывается, когда токен сброса пароля просрочен.
    """

    def __init__(self) -> None:
        """EN: Create an error for an expired password reset token.

        RU: Создаёт ошибку для просроченного reset token.
        """

        super().__init__(
            message="Токен истёк",
            event_type="reset_token_expired"
        )
