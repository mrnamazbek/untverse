from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, HttpUrl


class SupportedLocale(str, Enum):
    KK = "kk"
    RU = "ru"
    EN = "en"


class AuthProvider(str, Enum):
    GOOGLE = "google"
    PASSWORD = "password"
    APPLE = "apple"
    GITHUB = "github"


class AuthErrorCode(str, Enum):
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"
    AUTH_USER_INACTIVE = "AUTH_USER_INACTIVE"
    AUTH_PASSWORD_NOT_SET = "AUTH_PASSWORD_NOT_SET"
    AUTH_EMAIL_ALREADY_EXISTS = "AUTH_EMAIL_ALREADY_EXISTS"
    AUTH_OAUTH_INIT_FAILED = "AUTH_OAUTH_INIT_FAILED"
    AUTH_OAUTH_STATE_INVALID = "AUTH_OAUTH_STATE_INVALID"
    AUTH_OAUTH_STATE_EXPIRED = "AUTH_OAUTH_STATE_EXPIRED"
    AUTH_OAUTH_CODE_EXCHANGE_FAILED = "AUTH_OAUTH_CODE_EXCHANGE_FAILED"
    AUTH_OAUTH_EMAIL_UNVERIFIED = "AUTH_OAUTH_EMAIL_UNVERIFIED"
    AUTH_SESSION_EXPIRED = "AUTH_SESSION_EXPIRED"
    AUTH_SESSION_REVOKED = "AUTH_SESSION_REVOKED"
    AUTH_SESSION_REUSE_DETECTED = "AUTH_SESSION_REUSE_DETECTED"
    AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    AUTH_INVALID_REDIRECT_URI = "AUTH_INVALID_REDIRECT_URI"
    AUTH_CANNOT_UNLINK_LAST_PROVIDER = "AUTH_CANNOT_UNLINK_LAST_PROVIDER"


# --- OAuth 2.0 PKCE Schemas ---

class OAuthInitRequest(BaseModel):
    locale: SupportedLocale = Field(default=SupportedLocale.RU, description="Язык интерфейса (kk, ru, en)")
    redirect_to: Optional[str] = Field(default="/dashboard", description="Относительный URL для возврата пользователя после входа")


class OAuthInitResponse(BaseModel):
    authorization_url: str = Field(..., description="Google OAuth 2.0 URL с параметрами PKCE и state")
    state: str = Field(..., description="Криптографически подписанный JWT state (HS256)")


class OAuthCallbackRequest(BaseModel):
    code: str = Field(..., description="Authorization code, полученный от Google")
    state: str = Field(..., description="Подписанный JWT state для валидации и распаковки PKCE code_verifier")


# --- User & Account Schemas ---

class AuthAccountResponse(BaseModel):
    id: int
    provider: str
    provider_account_id: str
    provider_email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileDetails(BaseModel):
    id: int
    user_id: int
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    target_unt_score: int
    current_level: int
    total_xp: int
    rank_title: str
    streak_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FullUserResponse(BaseModel):
    id: int
    email: EmailStr
    email_verified: bool
    is_active: bool
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    profile: Optional[UserProfileDetails] = None
    auth_accounts: Optional[List[AuthAccountResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# --- Token Schemas ---

class UnifiedTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=900, description="TTL access-токена в секундах (15 мин)")
    user_id: int
    email: str
    role: str
    display_name: str
    current_level: int
    total_xp: int
    rank_title: str
    streak_count: int
    avatar_url: Optional[str] = None
    redirect_to: Optional[str] = None


class GoogleLoginResponse(UnifiedTokenResponse):
    is_new_user: bool = Field(default=False, description="Признак первого входа / регистрации пользователя")


class LocalTokenRefreshRequest(BaseModel):
    refresh_token: Optional[str] = Field(None, description="Опционально передается в теле, если не используется HttpOnly cookie")


class SetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100, description="Новый пароль учетной записи")


# --- Error Schemas ---

class LocalizedErrorMessage(BaseModel):
    kk: str
    ru: str
    en: str


class LocalizedErrorResponse(BaseModel):
    code: AuthErrorCode
    message: str = Field(..., description="Локализованное сообщение на языке клиента")
    localized: LocalizedErrorMessage
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
