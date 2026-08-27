from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.models.user import User, UserProfile
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
)
from app.core.exceptions import BadRequestException, UnauthorizedException, ConflictException
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserProfileResponse


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, user_in: UserCreate) -> TokenResponse:
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ConflictException(detail="Пользователь с таким email уже зарегистрирован")

        hashed_password = get_password_hash(user_in.password)
        user = await self.user_repo.create_user_with_profile(
            email=user_in.email,
            hashed_password=hashed_password,
            display_name=user_in.display_name,
            role=user_in.role or "student"
        )

        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str = create_refresh_token(subject=user.id)
        
        # Save refresh token in DB
        decoded_refresh = decode_token(refresh_token_str)
        exp_timestamp = decoded_refresh["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        await self.user_repo.save_refresh_token(user.id, refresh_token_str, expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=user.profile.display_name,
            current_level=user.profile.current_level,
            total_xp=user.profile.total_xp,
            rank_title=user.profile.rank_title,
            streak_count=user.profile.streak_count,
        )

    async def login(self, login_in: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise UnauthorizedException(detail="Неверный email или пароль")

        if not user.is_active:
            raise BadRequestException(detail="Аккаунт деактивирован")

        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str = create_refresh_token(subject=user.id)

        decoded_refresh = decode_token(refresh_token_str)
        exp_timestamp = decoded_refresh["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        await self.user_repo.save_refresh_token(user.id, refresh_token_str, expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=user.profile.display_name if user.profile else user.email.split("@")[0],
            current_level=user.profile.current_level if user.profile else 1,
            total_xp=user.profile.total_xp if user.profile else 0,
            rank_title=user.profile.rank_title if user.profile else "Новичок Информатики",
            streak_count=user.profile.streak_count if user.profile else 0,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        token_record = await self.user_repo.get_valid_refresh_token(refresh_token)
        if not token_record:
            raise UnauthorizedException(detail="Недействительный или отозванный refresh токен")

        decoded = decode_token(refresh_token)
        if not decoded or decoded.get("type") != "refresh":
            raise UnauthorizedException(detail="Некорректная сигнатура токена")

        user_id = int(decoded["sub"])
        user = await self.user_repo.get_with_profile(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException(detail="Пользователь не найден")

        # Revoke old refresh token (rotation)
        await self.user_repo.revoke_refresh_token(refresh_token)

        # Issue new pair
        new_access_token = create_access_token(subject=user.id, role=user.role)
        new_refresh_token_str = create_refresh_token(subject=user.id)

        decoded_new_refresh = decode_token(new_refresh_token_str)
        exp_timestamp = decoded_new_refresh["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        await self.user_repo.save_refresh_token(user.id, new_refresh_token_str, expires_at)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token_str,
            user_id=user.id,
            email=user.email,
            role=user.role,
            display_name=user.profile.display_name if user.profile else user.email,
            current_level=user.profile.current_level if user.profile else 1,
            total_xp=user.profile.total_xp if user.profile else 0,
            rank_title=user.profile.rank_title if user.profile else "Новичок Информатики",
            streak_count=user.profile.streak_count if user.profile else 0,
        )

    async def logout(self, refresh_token: str) -> bool:
        if refresh_token:
            await self.user_repo.revoke_refresh_token(refresh_token)
        return True
