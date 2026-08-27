from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.models.user import User, UserProfile, RefreshToken
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).options(selectinload(User.profile)).where(User.email == email.lower())
        )
        return result.scalars().first()

    async def get_with_profile(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).options(selectinload(User.profile)).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create_user_with_profile(self, email: str, hashed_password: str, display_name: str, role: str = "student") -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            role=role,
            is_active=True,
            is_verified=True,
        )
        self.session.add(user)
        await self.session.flush()

        profile = UserProfile(
            user_id=user.id,
            display_name=display_name,
            target_unt_score=50,
            current_level=1,
            total_xp=0,
            rank_title="Новичок Информатики",
            streak_count=0,
        )
        self.session.add(profile)
        await self.session.flush()
        return await self.get_with_profile(user.id)

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False
        )
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_valid_refresh_token(self, token: str) -> Optional[RefreshToken]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now
            )
        )
        return result.scalars().first()

    async def revoke_refresh_token(self, token: str) -> bool:
        result = await self.session.execute(
            update(RefreshToken).where(RefreshToken.token == token).values(revoked=True)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def update_profile(self, user_id: int, **kwargs) -> Optional[UserProfile]:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalars().first()
        if not profile:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile
