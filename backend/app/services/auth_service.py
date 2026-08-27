import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.core.exceptions import (
    AuthException,
    BadRequestException,
    UnauthorizedException,
    ConflictException,
    NotFoundException,
)
from app.models.user import User, UserProfile
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    AuthErrorCode,
    UnifiedTokenResponse,
    GoogleLoginResponse,
    FullUserResponse,
)
from app.schemas.user import UserCreate, UserLogin, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(
        self,
        user_in: UserCreate,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UnifiedTokenResponse:
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise AuthException(
                code=AuthErrorCode.AUTH_EMAIL_ALREADY_EXISTS,
                status_code=409,
                detail="Пользователь с таким email уже зарегистрирован",
            )

        hashed_password = get_password_hash(user_in.password)
        user = await self.user_repo.create_user_with_profile(
            email=user_in.email,
            hashed_password=hashed_password,
            display_name=user_in.display_name,
            # Roles are an administrator-owned authorization boundary. Public
            # registration must never be able to mint teacher/admin accounts.
            role="student",
            is_verified=True,
            email_verified=False,
        )

        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str = create_refresh_token(subject=user.id)
        token_hash_val = hash_token(refresh_token_str)

        decoded_refresh = decode_token(refresh_token_str)
        exp_timestamp = decoded_refresh["exp"] if decoded_refresh and "exp" in decoded_refresh else (
            datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ).timestamp()
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # Save to rotating RefreshSession table (SHA-256 hash)
        await self.user_repo.save_refresh_session(
            user_id=user.id,
            token_hash=token_hash_val,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self.user_repo.update_last_login(user.id)

        profile = user.profile
        return UnifiedTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=15 * 60,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=profile.display_name if profile else user_in.display_name,
            current_level=profile.current_level if profile else 1,
            total_xp=profile.total_xp if profile else 0,
            rank_title=profile.rank_title if profile else "Новичок Информатики",
            streak_count=profile.streak_count if profile else 0,
            avatar_url=profile.avatar_url if profile else None,
            redirect_to="/dashboard",
        )

    async def login(
        self,
        login_in: UserLogin,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UnifiedTokenResponse:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user:
            raise AuthException(
                code=AuthErrorCode.AUTH_INVALID_CREDENTIALS,
                status_code=401,
                detail="Неверный email или пароль",
            )

        # Handle account registered only through Google OAuth without password
        if user.hashed_password is None:
            raise AuthException(
                code=AuthErrorCode.AUTH_PASSWORD_NOT_SET,
                status_code=400,
                detail="Для аккаунта не задан пароль. Войдите через Google или воспользуйтесь восстановлением доступа",
            )

        if not verify_password(login_in.password, user.hashed_password):
            raise AuthException(
                code=AuthErrorCode.AUTH_INVALID_CREDENTIALS,
                status_code=401,
                detail="Неверный email или пароль",
            )

        if not user.is_active:
            raise AuthException(
                code=AuthErrorCode.AUTH_USER_INACTIVE,
                status_code=400,
                detail="Ваш аккаунт деактивирован",
            )

        await self.user_repo.update_last_login(user.id)

        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str = create_refresh_token(subject=user.id)
        token_hash_val = hash_token(refresh_token_str)

        decoded_refresh = decode_token(refresh_token_str)
        exp_timestamp = decoded_refresh["exp"] if decoded_refresh and "exp" in decoded_refresh else (
            datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ).timestamp()
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        await self.user_repo.save_refresh_session(
            user_id=user.id,
            token_hash=token_hash_val,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        profile = user.profile
        return UnifiedTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=15 * 60,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=profile.display_name if profile else user.email.split("@")[0],
            current_level=profile.current_level if profile else 1,
            total_xp=profile.total_xp if profile else 0,
            rank_title=profile.rank_title if profile else "Новичок Информатики",
            streak_count=profile.streak_count if profile else 0,
            avatar_url=profile.avatar_url if profile else None,
            redirect_to="/dashboard",
        )

    async def authenticate_or_register_google(
        self,
        user_info: Dict[str, Any],
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        redirect_to: Optional[str] = "/dashboard",
    ) -> GoogleLoginResponse:
        """
        Unified Google OAuth 2.0 Account Linking and Provisioning:
        1. Sub lookup in auth_accounts (google, sub).
        2. If not found, lookup User by email (if email_verified==True) -> Safe linking.
        3. If not found, atomic creation of User + UserProfile + AuthAccount + Streak + UserRole.
        4. Issues Access Token (15m) + Refresh Token (30d) and persists SHA-256 session hash.
        """
        google_sub = user_info.get("sub")
        email = user_info.get("email", "").lower().strip()
        email_verified = user_info.get("email_verified", False)
        display_name = user_info.get("name") or email.split("@")[0]
        avatar_url = user_info.get("picture")

        if not email or not google_sub:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED,
                status_code=400,
                detail="Некорректные данные профиля Google (отсутствует sub или email)",
            )

        if not email_verified:
            raise AuthException(
                code=AuthErrorCode.AUTH_OAUTH_EMAIL_UNVERIFIED,
                status_code=400,
                detail="Email в аккаунте Google не подтвержден. Привязка невозможна",
            )

        is_new_user = False

        # Step 1: Find by AuthAccount (provider="google", provider_account_id=sub)
        auth_account = await self.user_repo.get_by_provider("google", google_sub)
        if auth_account:
            user = auth_account.user
            if not user.is_active:
                raise AuthException(
                    code=AuthErrorCode.AUTH_USER_INACTIVE,
                    status_code=400,
                    detail="Ваш аккаунт деактивирован",
                )
            if auth_account.provider_email != email:
                auth_account.provider_email = email
            if not user.email_verified:
                await self.user_repo.mark_email_verified(user.id)
            if user.profile and not user.profile.avatar_url and avatar_url:
                await self.user_repo.update_profile(user.id, avatar_url=avatar_url)
        else:
            # Step 2: Search existing user by email
            existing_user = await self.user_repo.get_by_email(email)
            if existing_user:
                if not existing_user.is_active:
                    raise AuthException(
                        code=AuthErrorCode.AUTH_USER_INACTIVE,
                        status_code=400,
                        detail="Ваш аккаунт деактивирован",
                    )
                # Linking by email is safe only for an email that the existing
                # account has already proved it controls. Otherwise a malicious
                # pre-registration could capture a victim's first Google login.
                if not existing_user.email_verified:
                    raise AuthException(
                        code=AuthErrorCode.AUTH_EMAIL_ALREADY_EXISTS,
                        status_code=409,
                        detail="Этот email уже занят неподтвержденной учетной записью. Обратитесь в поддержку для восстановления доступа",
                    )
                # Link Google auth account
                await self.user_repo.link_account(
                    user_id=existing_user.id,
                    provider="google",
                    provider_account_id=google_sub,
                    provider_email=email,
                )
                if not existing_user.email_verified:
                    await self.user_repo.mark_email_verified(existing_user.id)
                if existing_user.profile and not existing_user.profile.avatar_url and avatar_url:
                    await self.user_repo.update_profile(existing_user.id, avatar_url=avatar_url)
                user = await self.user_repo.get_with_profile(existing_user.id)
            else:
                # Step 3: Atomic Provisioning for new user
                is_new_user = True
                user = await self.user_repo.create_user_with_profile(
                    email=email,
                    hashed_password=None,
                    display_name=display_name,
                    role="student",
                    is_verified=True,
                    email_verified=True,
                )
                await self.user_repo.link_account(
                    user_id=user.id,
                    provider="google",
                    provider_account_id=google_sub,
                    provider_email=email,
                )
                if avatar_url:
                    await self.user_repo.update_profile(user.id, avatar_url=avatar_url)
                user = await self.user_repo.get_with_profile(user.id)

        # Update last login timestamp
        await self.user_repo.update_last_login(user.id)

        # Generate tokens
        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str = create_refresh_token(subject=user.id)
        token_hash_val = hash_token(refresh_token_str)

        decoded_refresh = decode_token(refresh_token_str)
        exp_timestamp = decoded_refresh["exp"] if decoded_refresh and "exp" in decoded_refresh else (
            datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ).timestamp()
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # Save to RefreshSession (SHA-256 hash)
        await self.user_repo.save_refresh_session(
            user_id=user.id,
            token_hash=token_hash_val,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        profile = user.profile
        return GoogleLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=15 * 60,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=profile.display_name if profile else display_name,
            current_level=profile.current_level if profile else 1,
            total_xp=profile.total_xp if profile else 0,
            rank_title=profile.rank_title if profile else "Новичок Информатики",
            streak_count=profile.streak_count if profile else 0,
            avatar_url=profile.avatar_url if profile else avatar_url,
            redirect_to=redirect_to or "/dashboard",
            is_new_user=is_new_user,
        )

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UnifiedTokenResponse:
        """
        Token Rotation & Replay Detection:
        - Computes SHA-256 hash of the incoming token.
        - If session is found and revoked==True -> REUSE DETECTED -> revoke all user sessions.
        - If session is found and active -> revoke old session, link replaced_by_hash, issue new pair.
        """
        if not raw_refresh_token:
            raise AuthException(
                code=AuthErrorCode.AUTH_UNAUTHORIZED,
                status_code=401,
                detail="Refresh токен не передан",
            )

        decoded = decode_token(raw_refresh_token)
        if not decoded or decoded.get("type") != "refresh":
            raise AuthException(
                code=AuthErrorCode.AUTH_UNAUTHORIZED,
                status_code=401,
                detail="Недействительный токен или некорректная сигнатура",
            )

        token_hash_val = hash_token(raw_refresh_token)
        session = await self.user_repo.get_session_by_hash(token_hash_val)

        if session:
            # Replay Detection: If already revoked, token was reused (possible theft)
            if session.revoked:
                # Immediate security protocol: revoke ALL sessions of this user
                await self.user_repo.revoke_all_user_sessions(session.user_id)
                raise AuthException(
                    code=AuthErrorCode.AUTH_SESSION_REUSE_DETECTED,
                    status_code=401,
                    detail="Обнаружена попытка повторного использования сессии. Все устройства отключены в целях безопасности",
                )

            # Check expiration
            now = datetime.now(timezone.utc)
            sess_exp = session.expires_at if session.expires_at.tzinfo else session.expires_at.replace(tzinfo=timezone.utc)
            if sess_exp < now:
                raise AuthException(
                    code=AuthErrorCode.AUTH_SESSION_EXPIRED,
                    status_code=401,
                    detail="Сессия завершена. Пожалуйста, выполните повторный вход",
                )

            user_id = session.user_id
        else:
            raise AuthException(
                code=AuthErrorCode.AUTH_SESSION_EXPIRED,
                status_code=401,
                detail="Недействительный или отозванный refresh токен",
            )

        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            raise AuthException(
                code=AuthErrorCode.AUTH_USER_NOT_FOUND,
                status_code=401,
                detail="Пользователь не найден",
            )
        if not user.is_active:
            raise AuthException(
                code=AuthErrorCode.AUTH_USER_INACTIVE,
                status_code=401,
                detail="Ваш аккаунт деактивирован",
            )

        # Issue new token pair
        new_access_token = create_access_token(subject=user.id, role=user.role)
        new_refresh_token_str = create_refresh_token(subject=user.id)
        new_token_hash_val = hash_token(new_refresh_token_str)

        decoded_new = decode_token(new_refresh_token_str)
        new_exp_ts = decoded_new["exp"] if decoded_new and "exp" in decoded_new else (
            datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ).timestamp()
        new_expires_at = datetime.fromtimestamp(new_exp_ts, tz=timezone.utc)

        # Invalidate old session and link to new session hash
        if session:
            await self.user_repo.revoke_session_by_hash(
                token_hash=token_hash_val,
                replaced_by_hash=new_token_hash_val,
            )

        # Create new active session
        await self.user_repo.save_refresh_session(
            user_id=user.id,
            token_hash=new_token_hash_val,
            expires_at=new_expires_at,
            user_agent=user_agent or (session.user_agent if session else None),
            ip_address=ip_address or (session.ip_address if session else None),
        )

        profile = user.profile
        return UnifiedTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token_str,
            token_type="bearer",
            expires_in=15 * 60,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=profile.display_name if profile else user.email.split("@")[0],
            current_level=profile.current_level if profile else 1,
            total_xp=profile.total_xp if profile else 0,
            rank_title=profile.rank_title if profile else "Новичок Информатики",
            streak_count=profile.streak_count if profile else 0,
            avatar_url=profile.avatar_url if profile else None,
            redirect_to="/dashboard",
        )

    async def logout(self, raw_token: Optional[str]) -> bool:
        """
        Revoke specific refresh session by raw token SHA-256 hash.
        """
        if not raw_token:
            return True
        token_hash_val = hash_token(raw_token)
        await self.user_repo.revoke_session_by_hash(token_hash_val)
        return True

    async def logout_all(self, user_id: int) -> int:
        """
        Revoke all active sessions for a specific user.
        """
        count = await self.user_repo.revoke_all_user_sessions(user_id)
        return count

    async def set_password(self, user_id: int, new_password: str) -> bool:
        """
        Set local password for user (e.g. registered via Google OAuth).
        Uses Argon2id hashing and records password provider in auth_accounts.
        """
        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            raise AuthException(
                code=AuthErrorCode.AUTH_USER_NOT_FOUND,
                status_code=404,
                detail="Пользователь не найден",
            )

        if not new_password or len(new_password) < 8:
            raise AuthException(
                code=AuthErrorCode.AUTH_INVALID_CREDENTIALS,
                status_code=400,
                detail="Пароль должен содержать не менее 8 символов",
            )

        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password

        # Link password provider in auth_accounts if not present
        await self.user_repo.link_account(
            user_id=user.id,
            provider="password",
            provider_account_id=user.email,
            provider_email=user.email,
        )
        await self.session.flush()
        return True
