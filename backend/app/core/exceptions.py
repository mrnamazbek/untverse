from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.schemas.auth import AuthErrorCode


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "You do not have permission to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


AUTH_ERROR_MESSAGES: dict[str, dict[str, str]] = {
    AuthErrorCode.AUTH_INVALID_CREDENTIALS.value: {
        "ru": "Неверный email или пароль",
        "kk": "Email немесе құпиясөз қате",
        "en": "Invalid email or password",
    },
    AuthErrorCode.AUTH_USER_NOT_FOUND.value: {
        "ru": "Пользователь не найден",
        "kk": "Пайдаланушы табылмады",
        "en": "User not found",
    },
    AuthErrorCode.AUTH_USER_INACTIVE.value: {
        "ru": "Ваш аккаунт деактивирован",
        "kk": "Сіздің аккаунтыңыз бұғатталған",
        "en": "Your account has been deactivated",
    },
    AuthErrorCode.AUTH_PASSWORD_NOT_SET.value: {
        "ru": "Для аккаунта не задан пароль. Войдите через Google или воспользуйтесь восстановлением доступа",
        "kk": "Аккаунтқа құпиясөз орнатылмаған. Google арқылы кіріңіз немесе кіруді қалпына келтіріңіз",
        "en": "Password is not set for this account. Please sign in with Google",
    },
    AuthErrorCode.AUTH_EMAIL_ALREADY_EXISTS.value: {
        "ru": "Пользователь с таким email уже зарегистрирован",
        "kk": "Бұл email бар пайдаланушы тіркелген",
        "en": "A user with this email already exists",
    },
    AuthErrorCode.AUTH_OAUTH_INIT_FAILED.value: {
        "ru": "Ошибка инициализации Google OAuth",
        "kk": "Google OAuth инициализациясының қатесі",
        "en": "Failed to initialize Google OAuth",
    },
    AuthErrorCode.AUTH_OAUTH_STATE_INVALID.value: {
        "ru": "Недействительная подпись сессии авторизации",
        "kk": "Авторизация сессиясының қолтаңбасы жарамсыз",
        "en": "Invalid authorization session state",
    },
    AuthErrorCode.AUTH_OAUTH_STATE_EXPIRED.value: {
        "ru": "Время ожидания авторизации истекло (10 мин). Повторите попытку",
        "kk": "Авторизацияны күту уақыты аяқталды (10 мин). Қайталап көріңіз",
        "en": "Authorization session expired. Please try again",
    },
    AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED.value: {
        "ru": "Ошибка обмена авторизационного кода Google",
        "kk": "Google авторизация кодын алмасу қатесі",
        "en": "Failed to exchange Google authorization code",
    },
    AuthErrorCode.AUTH_OAUTH_EMAIL_UNVERIFIED.value: {
        "ru": "Email в аккаунте Google не подтвержден. Привязка невозможна",
        "kk": "Google аккаунтындағы email расталмаған. Байланыстыру мүмкін емес",
        "en": "Google email is unverified. Account linking rejected",
    },
    AuthErrorCode.AUTH_SESSION_EXPIRED.value: {
        "ru": "Сессия завершена. Пожалуйста, выполните повторный вход",
        "kk": "Сессия аяқталды. Қайта кіруіңізді сұраймыз",
        "en": "Session expired. Please log in again",
    },
    AuthErrorCode.AUTH_SESSION_REVOKED.value: {
        "ru": "Сессия была отозвана",
        "kk": "Сессия кері қайтарылды",
        "en": "Session was revoked",
    },
    AuthErrorCode.AUTH_SESSION_REUSE_DETECTED.value: {
        "ru": "Обнаружена попытка повторного использования сессии. Все устройства отключены в целях безопасности",
        "kk": "Сессияны қайталап пайдалану әрекеті анықталды. Қауіпсіздік үшін барлық құрылғылар ажыратылды",
        "en": "Token reuse detected. All sessions revoked for security",
    },
    AuthErrorCode.AUTH_UNAUTHORIZED.value: {
        "ru": "Требуется авторизация",
        "kk": "Авторизация қажет",
        "en": "Authentication required",
    },
    AuthErrorCode.AUTH_FORBIDDEN.value: {
        "ru": "Доступ запрещен",
        "kk": "Қолжетімділікке тыйым салынған",
        "en": "Access forbidden",
    },
    AuthErrorCode.AUTH_INVALID_REDIRECT_URI.value: {
        "ru": "Недопустимый адрес перенаправления",
        "kk": "Рұқсат етілмеген қайта бағыттау мекенжайы",
        "en": "Invalid redirect URI",
    },
    AuthErrorCode.AUTH_CANNOT_UNLINK_LAST_PROVIDER.value: {
        "ru": "Нельзя отвязать единственный способ входа",
        "kk": "Жалғыз кіру әдісін ажыратуға болмайды",
        "en": "Cannot unlink the only login method",
    },
}


class AuthException(AppException):
    def __init__(
        self,
        code: AuthErrorCode,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        locale: str = "ru",
        detail: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        code_str = code.value if isinstance(code, AuthErrorCode) else str(code)
        loc_dict = AUTH_ERROR_MESSAGES.get(code_str, {
            "ru": "Ошибка аутентификации",
            "kk": "Аутентификация қатесі",
            "en": "Authentication error",
        })
        lang = locale if locale in ("kk", "ru", "en") else "ru"
        msg = detail or loc_dict.get(lang, loc_dict["ru"])
        self.code = code_str
        self.code_enum = code if isinstance(code, AuthErrorCode) else AuthErrorCode(code_str)
        self.localized = loc_dict
        self.details = details or {}
        self.message = msg
        super().__init__(status_code=status_code, detail=msg)
