import urllib.parse
from typing import Optional
from fastapi import APIRouter, Depends, Response, Request, status, Cookie, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.oauth_service import GoogleOAuthService
from app.schemas.auth import (
    SupportedLocale,
    OAuthInitResponse,
    OAuthCallbackRequest,
    GoogleLoginResponse,
    UnifiedTokenResponse,
    LocalTokenRefreshRequest,
    SetPasswordRequest,
    FullUserResponse,
    AuthErrorCode,
)
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.core.exceptions import AuthException

router = APIRouter()


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    access_max_age: int = 15 * 60,
    refresh_max_age: int = 30 * 24 * 3600,
) -> None:
    """Set secure HttpOnly cookies for access and refresh tokens."""
    domain = settings.AUTH_COOKIE_DOMAIN or None
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=domain,
        path="/",
        max_age=access_max_age,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=domain,
        path="/",
        max_age=refresh_max_age,
    )


def clear_auth_cookies(response: Response) -> None:
    """Delete authentication cookies."""
    domain = settings.AUTH_COOKIE_DOMAIN or None
    response.delete_cookie(
        key="access_token",
        domain=domain,
        path="/",
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key="refresh_token",
        domain=domain,
        path="/",
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


def set_oauth_transaction_cookie(response: Response, transaction: str) -> None:
    response.set_cookie(
        key="oauth_transaction",
        value=transaction,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="lax",
        domain=settings.AUTH_COOKIE_DOMAIN or None,
        path="/api/v1/auth",
        max_age=10 * 60,
    )


def clear_oauth_transaction_cookie(response: Response) -> None:
    response.delete_cookie(
        key="oauth_transaction",
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="lax",
        domain=settings.AUTH_COOKIE_DOMAIN or None,
        path="/api/v1/auth",
    )


# --- Google OAuth 2.0 PKCE Endpoints ---

@router.get("/oauth/google/init", response_model=OAuthInitResponse, summary="Инициализация Google OAuth 2.0 PKCE")
@router.get("/google/login", response_model=OAuthInitResponse, summary="Алиас инициализации Google OAuth")
async def google_oauth_init(
    response: Response,
    locale: SupportedLocale = Query(default=SupportedLocale.RU, description="Язык интерфейса"),
    redirect_to: Optional[str] = Query(default="/dashboard", description="Относительный URL для перенаправления"),
):
    """
    Генерирует криптографически стойкую пару PKCE (S256) и подписанный JWT state (HS256, 10 мин),
    возвращая Authorization URL на Google Identity Services.
    """
    auth_url, state, transaction = GoogleOAuthService.get_authorization_url(
        locale=locale.value,
        redirect_to=redirect_to or "/dashboard",
    )
    set_oauth_transaction_cookie(response, transaction)
    return OAuthInitResponse(authorization_url=auth_url, state=state)


@router.post("/oauth/google/callback", response_model=GoogleLoginResponse, summary="REST Callback Google OAuth 2.0")
@router.post("/google/callback", response_model=GoogleLoginResponse, summary="REST Callback Google OAuth (алиас)")
async def google_oauth_callback(
    callback_in: OAuthCallbackRequest,
    request: Request,
    response: Response,
    oauth_transaction: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Принимает code и подписанный JWT state из фронтенд-приложения:
    1. Верифицирует JWT state и извлекает PKCE code_verifier, locale, redirect_to.
    2. Выполняет безопасный обмен code + code_verifier на токены Google.
    3. Верифицирует Google ID Token и связывает/создает аккаунт.
    4. Устанавливает HttpOnly cookies и возвращает DTO с токенами.
    """
    state_data = GoogleOAuthService.verify_and_decode_state(callback_in.state)
    if not oauth_transaction:
        raise AuthException(code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID, status_code=400, detail="Сессия OAuth не найдена")
    code_verifier = GoogleOAuthService.verify_oauth_transaction(oauth_transaction, callback_in.state)
    redirect_to = state_data.get("redirect_to", "/dashboard")

    tokens = await GoogleOAuthService.exchange_code_for_tokens(
        code=callback_in.code,
        code_verifier=code_verifier,
    )
    id_token = tokens.get("id_token")
    if not id_token:
        raise AuthException(
            code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
            status_code=400,
            detail="В ответе Google отсутствует id_token",
        )

    user_info = GoogleOAuthService.verify_id_token(id_token, expected_nonce=state_data["nonce"])

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    service = AuthService(db)
    login_resp = await service.authenticate_or_register_google(
        user_info=user_info,
        user_agent=user_agent,
        ip_address=ip_address,
        redirect_to=redirect_to,
    )
    await db.commit()

    set_auth_cookies(response, login_resp.access_token, login_resp.refresh_token)
    clear_oauth_transaction_cookie(response)
    return login_resp


@router.get("/oauth/google/callback", summary="Обработка браузерного редиректа от Google")
@router.get("/google/callback", summary="Обработка браузерного редиректа от Google (алиас)")
async def google_oauth_browser_callback(
    request: Request,
    code: Optional[str] = Query(default=None, description="Код авторизации Google"),
    state: Optional[str] = Query(default=None, description="Подписанный JWT state"),
    error: Optional[str] = Query(default=None, description="Код ошибки от Google"),
    error_description: Optional[str] = Query(default=None, description="Описание ошибки от Google"),
    oauth_transaction: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Обрабатывает прямой GET-редирект браузера от Google Identity Provider:
    Устанавливает HttpOnly cookies и делает 307-редирект на Next.js фронтенд.
    """
    locale = "ru"
    if error or not code or not state:
        if state:
            try:
                state_data = GoogleOAuthService.verify_and_decode_state(state)
                locale = state_data.get("locale", "ru")
            except Exception:
                pass
        err_msg = error_description or error or "Отсутствует код авторизации"
        err_url = f"{settings.FRONTEND_URL}/{locale}/auth/error?error={urllib.parse.quote(err_msg, safe='')}"
        return RedirectResponse(url=err_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        state_data = GoogleOAuthService.verify_and_decode_state(state)
        if not oauth_transaction:
            raise AuthException(code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID, status_code=400, detail="Сессия OAuth не найдена")
        locale = state_data.get("locale", "ru")
        redirect_to = state_data.get("redirect_to", "/dashboard")

        tokens = await GoogleOAuthService.exchange_code_for_tokens(
            code=code,
            code_verifier=GoogleOAuthService.verify_oauth_transaction(oauth_transaction, state),
        )
        id_token = tokens.get("id_token")
        if not id_token:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=400,
                detail="В ответе Google отсутствует id_token",
            )

        user_info = GoogleOAuthService.verify_id_token(id_token, expected_nonce=state_data["nonce"])
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        service = AuthService(db)
        login_resp = await service.authenticate_or_register_google(
            user_info=user_info,
            user_agent=user_agent,
            ip_address=ip_address,
            redirect_to=redirect_to,
        )
        await db.commit()

        target_url = f"{settings.FRONTEND_URL}/{locale}/auth/callback?redirect_to={urllib.parse.quote(redirect_to, safe='')}"
        redirect_resp = RedirectResponse(url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        set_auth_cookies(redirect_resp, login_resp.access_token, login_resp.refresh_token)
        clear_oauth_transaction_cookie(redirect_resp)
        return redirect_resp

    except AuthException as e:
        err_url = f"{settings.FRONTEND_URL}/{locale}/auth/error?code={e.code}&message={urllib.parse.quote(e.message, safe='')}"
        return RedirectResponse(url=err_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except Exception as e:
        err_url = f"{settings.FRONTEND_URL}/{locale}/auth/error?code=AUTH_OAUTH_CODE_EXCHANGE_FAILED&message={urllib.parse.quote('Google authorization could not be completed', safe='')}"
        return RedirectResponse(url=err_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# --- Standard Authentication Endpoints ---

@router.post("/register", response_model=UnifiedTokenResponse, status_code=status.HTTP_201_CREATED, summary="Регистрация по email и паролю")
async def register(
    user_in: UserCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    service = AuthService(db)
    token_resp = await service.register(user_in, user_agent=user_agent, ip_address=ip_address)
    await db.commit()

    set_auth_cookies(response, token_resp.access_token, token_resp.refresh_token)
    return token_resp


@router.post("/login", response_model=UnifiedTokenResponse, summary="Вход по email и паролю")
async def login(
    login_in: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    service = AuthService(db)
    token_resp = await service.login(login_in, user_agent=user_agent, ip_address=ip_address)
    await db.commit()

    set_auth_cookies(response, token_resp.access_token, token_resp.refresh_token)
    return token_resp


@router.post("/refresh", response_model=UnifiedTokenResponse, summary="Ротация сессии и обновление токенов")
async def refresh_tokens(
    request: Request,
    response: Response,
    refresh_in: Optional[LocalTokenRefreshRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
):
    token_str = None
    if refresh_in and refresh_in.refresh_token:
        token_str = refresh_in.refresh_token
    elif refresh_token_cookie:
        token_str = refresh_token_cookie

    if not token_str:
        raise AuthException(
            code=AuthErrorCode.AUTH_UNAUTHORIZED,
            status_code=401,
            detail="Refresh токен не передан в теле запроса или cookie",
        )

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    service = AuthService(db)
    token_resp = await service.refresh_tokens(token_str, user_agent=user_agent, ip_address=ip_address)
    await db.commit()

    set_auth_cookies(response, token_resp.access_token, token_resp.refresh_token)
    return token_resp


@router.post("/logout", summary="Выход из текущей сессии")
async def logout(
    response: Response,
    logout_in: Optional[LocalTokenRefreshRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
):
    token_str = logout_in.refresh_token if logout_in and logout_in.refresh_token else refresh_token_cookie
    if token_str:
        service = AuthService(db)
        await service.logout(token_str)
        await db.commit()

    clear_auth_cookies(response)
    return {"message": "Успешный выход из системы"}


@router.post("/logout-all", summary="Отзыв всех активных сессий пользователя")
async def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    revoked_count = await service.logout_all(current_user.id)
    await db.commit()

    clear_auth_cookies(response)
    return {
        "message": "Все активные сессии успешно завершены",
        "revoked_sessions_count": revoked_count,
    }


@router.post("/set-password", summary="Установка постоянного пароля для учетной записи")
async def set_password(
    body: SetPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.set_password(current_user.id, body.new_password)
    await db.commit()
    return {"message": "Пароль успешно установлен"}


@router.get("/me", response_model=FullUserResponse, summary="Получить профиль текущего авторизованного пользователя")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
