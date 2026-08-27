import base64
import hashlib
import re
import secrets
import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any

import httpx
from jose import jwt, JWTError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import settings
from app.core.exceptions import AuthException
from app.schemas.auth import AuthErrorCode, SupportedLocale


class GoogleOAuthService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

    # RFC 7636 and Open Redirect security regular expression
    SAFE_REDIRECT_REGEX = re.compile(r"^/(?!/)[a-zA-Z0-9_\-/.?=&%#]*$")

    @staticmethod
    def generate_pkce_challenge() -> Tuple[str, str]:
        """
        Generate PKCE code_verifier (86 chars URL-safe) and code_challenge (S256, base64url unpadded).
        RFC 7636 Section 4: verifier is 43-128 chars, entropy >= 256 bits.
        """
        code_verifier = secrets.token_urlsafe(64)  # 64 raw random bytes -> 86 chars
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        return code_verifier, code_challenge

    @classmethod
    def sanitize_redirect_url(cls, redirect_to: Optional[str]) -> str:
        """
        Open Redirect Protection:
        1. Must start with '/' and not '//'
        2. Must match SAFE_REDIRECT_REGEX
        3. Falls back to '/dashboard' if invalid
        """
        if not redirect_to or not isinstance(redirect_to, str):
            return "/dashboard"
        cleaned = redirect_to.strip()
        if not cls.SAFE_REDIRECT_REGEX.match(cleaned):
            return "/dashboard"
        return cleaned

    @classmethod
    def create_signed_state(
        cls,
        code_verifier: str,
        locale: str = "ru",
        redirect_to: str = "/dashboard",
        nonce: Optional[str] = None,
    ) -> str:
        """
        Create compact cryptographically signed JWT state (HS256) with 10 minutes TTL.
        Claims: loc, rd, nonce, iat, exp, typ='oauth_state', iss='untverse.kz'.
        The PKCE verifier is deliberately retained only in the HttpOnly
        transaction cookie, never in the state value sent to Google.
        """
        loc = locale if locale in ("kk", "ru", "en") else "ru"
        sanitized_redirect = cls.sanitize_redirect_url(redirect_to)
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=10)

        payload = {
            "loc": loc,
            "rd": sanitized_redirect,
            "nonce": nonce or str(uuid.uuid4()),
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "typ": "oauth_state",
            "iss": "untverse.kz",
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @classmethod
    def verify_and_decode_state(cls, state: str) -> Dict[str, Any]:
        """
        Verify signed JWT state, check expiration (exp <= 10m) and typ=='oauth_state'.
        Returns locale, redirect_to, and nonce. The verifier must be recovered
        from the signed HttpOnly transaction cookie.
        """
        if not state:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Параметр state отсутствует",
            )

        try:
            payload = jwt.decode(
                state,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except JWTError as e:
            error_str = str(e).lower()
            if "expired" in error_str:
                raise AuthException(
                    code=AuthErrorCode.AUTH_OAUTH_STATE_EXPIRED,
                    status_code=400,
                    detail="Время ожидания авторизации истекло (10 мин). Повторите попытку",
                )
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Недействительная подпись сессии авторизации",
            )
        except Exception:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Недействительная подпись сессии авторизации",
            )

        if payload.get("typ") != "oauth_state":
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Некорректный тип токена состояния",
            )

        locale = payload.get("loc", "ru")
        redirect_to = cls.sanitize_redirect_url(payload.get("rd"))

        return {
            "locale": locale,
            "redirect_to": redirect_to,
            "nonce": payload.get("nonce"),
        }

    @classmethod
    def create_oauth_transaction(cls, code_verifier: str, state: str) -> str:
        """Bind the PKCE verifier to the initiating browser in an HttpOnly cookie."""
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "cv": code_verifier,
                "st": state,
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=10)).timestamp()),
                "typ": "oauth_transaction",
                "iss": "untverse.kz",
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    def verify_oauth_transaction(cls, transaction: str, state: str) -> str:
        """Return a verifier only when the callback matches its initiating browser."""
        try:
            payload = jwt.decode(transaction, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Сессия авторизации недействительна или истекла",
            )
        if payload.get("typ") != "oauth_transaction" or not secrets.compare_digest(payload.get("st", ""), state):
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Сессия авторизации не соответствует callback",
            )
        verifier = payload.get("cv")
        if not verifier:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="В сессии авторизации отсутствует PKCE verifier",
            )
        return verifier

    @classmethod
    def get_authorization_url(
        cls,
        locale: str = "ru",
        redirect_to: str = "/dashboard",
    ) -> Tuple[str, str, str]:
        """
        Constructs Google OAuth 2.0 Authorization URL with PKCE (S256) and signed JWT state.
        Returns (authorization_url, public_state, signed_transaction_cookie).
        """
        client_id = settings.GOOGLE_CLIENT_ID
        if not client_id:
            if settings.ENVIRONMENT in ("test", "development"):
                client_id = "test-google-client-id.apps.googleusercontent.com"
            else:
                raise AuthException(
                    code=AuthErrorCode.AUTH_OAUTH_INIT_FAILED,
                    status_code=500,
                    locale=locale,
                    detail="GOOGLE_CLIENT_ID не настроен на сервере",
                )

        code_verifier, code_challenge = cls.generate_pkce_challenge()
        state = cls.create_signed_state(code_verifier, locale=locale, redirect_to=redirect_to)
        transaction = cls.create_oauth_transaction(code_verifier, state)

        params = {
            "client_id": client_id,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": state,
            "nonce": cls.verify_and_decode_state(state)["nonce"],
            "access_type": "offline",
            "prompt": "select_account",
        }
        url = f"{cls.GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
        return url, state, transaction

    @classmethod
    async def exchange_code_for_tokens(
        cls,
        code: str,
        code_verifier: str,
    ) -> Dict[str, Any]:
        """
        Asynchronously exchange authorization code and code_verifier for tokens at Google.
        """
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET

        if not client_id or not client_secret:
            if settings.ENVIRONMENT in ("test", "development"):
                client_id = client_id or "test-google-client-id.apps.googleusercontent.com"
                client_secret = client_secret or "test-google-client-secret"
            else:
                raise AuthException(
                    code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                    status_code=500,
                    detail="GOOGLE_CLIENT_ID или GOOGLE_CLIENT_SECRET не настроены на сервере",
                )

        data = {
            "code": code,
            "code_verifier": code_verifier,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(cls.GOOGLE_TOKEN_URL, data=data)
            except Exception as e:
                raise AuthException(
                    code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                    status_code=400,
                    detail=f"Ошибка соединения с сервером Google OAuth: {str(e)}",
                )

        if response.status_code != 200:
            error_details = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=400,
                detail=f"Ошибка обмена авторизационного кода Google: {error_details.get('error_description', response.text)}",
                details=error_details,
            )

        return response.json()

    @classmethod
    def verify_id_token(cls, id_token: str, expected_nonce: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify Google ID token and extract user profile information:
        sub, email, email_verified, name, picture.
        """
        if not id_token:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=400,
                detail="Отсутствует Google ID Token",
            )

        if not settings.GOOGLE_CLIENT_ID:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=500,
                detail="GOOGLE_CLIENT_ID не настроен на сервере",
            )
        try:
            payload = google_id_token.verify_oauth2_token(
                id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=400,
                detail="Google ID token не прошел проверку подписи, issuer, audience или срока действия",
            )

        if expected_nonce and not secrets.compare_digest(str(payload.get("nonce", "")), expected_nonce):
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_STATE_INVALID,
                status_code=400,
                detail="Nonce Google ID token не соответствует сессии авторизации",
            )

        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or not email:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=400,
                detail="ID token не содержит обязательных полей (sub, email)",
            )

        email_verified = payload.get("email_verified", False)
        if isinstance(email_verified, str):
            email_verified = email_verified.lower() == "true"

        if not email_verified:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_EMAIL_UNVERIFIED,
                status_code=400,
                detail="Email в аккаунте Google не подтвержден. Привязка невозможна",
            )

        name = payload.get("name") or payload.get("given_name") or email.split("@")[0]
        picture = payload.get("picture")

        return {
            "sub": str(sub),
            "email": str(email).lower().strip(),
            "email_verified": True,
            "name": str(name),
            "picture": picture,
        }
