from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.models.user import (
    User, UserProfile, Role, UserRole, UserRoleEnum,
    AuthAccount, RefreshSession, RefreshToken
)
from app.models.gamification import Streak
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.auth_accounts),
                selectinload(User.user_roles).selectinload(UserRole.role)
            )
            .where(User.email == email.lower())
        )
        return result.scalars().first()

    async def get_with_profile(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.auth_accounts),
                selectinload(User.user_roles).selectinload(UserRole.role)
            )
            .where(User.id == user_id)
        )
        return result.scalars().first()

    async def create_user_with_profile(
        self,
        email: str,
        hashed_password: Optional[str] = None,
        display_name: Optional[str] = None,
        role: str = "student",
        is_verified: bool = True,
        email_verified: bool = True,
    ) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            role=role,
            is_active=True,
            is_verified=is_verified,
            email_verified=email_verified,
        )
        self.session.add(user)
        await self.session.flush()

        profile_name = display_name or email.split("@")[0]
        profile = UserProfile(
            user_id=user.id,
            display_name=profile_name,
            target_unt_score=50,
            current_level=1,
            total_xp=0,
            rank_title="Новичок Информатики",
            streak_count=0,
        )
        self.session.add(profile)

        # If hashed_password is provided, register initial password auth account
        if hashed_password:
            auth_account = AuthAccount(
                user_id=user.id,
                provider="password",
                provider_account_id=email.lower(),
                provider_email=email.lower(),
            )
            self.session.add(auth_account)

        # Link normalized Role if available
        role_record = (await self.session.execute(
            select(Role).where(Role.name == role)
        )).scalars().first()
        if role_record:
            user_role = UserRole(user_id=user.id, role_id=role_record.id)
            self.session.add(user_role)

        # Initialize streak record
        streak = Streak(user_id=user.id, current_streak=0, longest_streak=0, freeze_count=0)
        self.session.add(streak)

        await self.session.flush()
        return await self.get_with_profile(user.id)

    # --- AuthAccount Methods ---

    async def get_by_provider(self, provider: str, provider_account_id: str) -> Optional[AuthAccount]:
        result = await self.session.execute(
            select(AuthAccount)
            .options(
                selectinload(AuthAccount.user).selectinload(User.profile),
                selectinload(AuthAccount.user).selectinload(User.auth_accounts),
                selectinload(AuthAccount.user).selectinload(User.user_roles).selectinload(UserRole.role)
            )
            .where(
                AuthAccount.provider == provider,
                AuthAccount.provider_account_id == provider_account_id
            )
        )
        return result.scalars().first()

    async def get_auth_accounts_by_user_id(self, user_id: int) -> List[AuthAccount]:
        result = await self.session.execute(
            select(AuthAccount).where(AuthAccount.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create_auth_account(
        self,
        user_id: int,
        provider: str,
        provider_account_id: str,
        provider_email: Optional[str] = None
    ) -> AuthAccount:
        auth_acc = AuthAccount(
            user_id=user_id,
            provider=provider,
            provider_account_id=provider_account_id,
            provider_email=provider_email.lower() if provider_email else None,
        )
        self.session.add(auth_acc)
        await self.session.flush()
        return auth_acc

    async def link_account(
        self,
        user_id: int,
        provider: str,
        provider_account_id: str,
        provider_email: Optional[str] = None
    ) -> AuthAccount:
        result = await self.session.execute(
            select(AuthAccount).where(
                AuthAccount.provider == provider,
                AuthAccount.provider_account_id == provider_account_id
            )
        )
        existing = result.scalars().first()
        if existing:
            if existing.user_id != user_id:
                raise ValueError("Данный аккаунт уже привязан к другому пользователю")
            if provider_email:
                existing.provider_email = provider_email.lower()
            await self.session.flush()
            return existing

        return await self.create_auth_account(
            user_id=user_id,
            provider=provider,
            provider_account_id=provider_account_id,
            provider_email=provider_email
        )

    async def unlink_account(self, user_id: int, provider: str) -> bool:
        result = await self.session.execute(
            delete(AuthAccount).where(
                AuthAccount.user_id == user_id,
                AuthAccount.provider == provider
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    # --- RefreshSession Methods (Hashed Token Sessions) ---

    async def save_refresh_session(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RefreshSession:
        session = RefreshSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            revoked=False
        )
        self.session.add(session)
        await self.session.flush()
        return session

    async def get_session_by_hash(self, token_hash: str) -> Optional[RefreshSession]:
        result = await self.session.execute(
            select(RefreshSession)
            .options(
                selectinload(RefreshSession.user).selectinload(User.profile),
                selectinload(RefreshSession.user).selectinload(User.auth_accounts),
                selectinload(RefreshSession.user).selectinload(User.user_roles).selectinload(UserRole.role)
            )
            .where(RefreshSession.token_hash == token_hash)
        )
        return result.scalars().first()

    async def revoke_session_by_hash(
        self,
        token_hash: str,
        replaced_by_hash: Optional[str] = None
    ) -> bool:
        now = datetime.now(timezone.utc)
        values = {"revoked": True, "revoked_at": now}
        if replaced_by_hash:
            values["replaced_by_hash"] = replaced_by_hash

        result = await self.session.execute(
            update(RefreshSession)
            .where(RefreshSession.token_hash == token_hash)
            .values(**values)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def revoke_all_user_sessions(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.user_id == user_id,
                RefreshSession.revoked == False
            )
            .values(revoked=True, revoked_at=now)
        )
        await self.session.flush()
        return result.rowcount

    # --- User Helpers ---

    async def update_last_login(self, user_id: int, last_login_at: Optional[datetime] = None) -> None:
        login_time = last_login_at or datetime.now(timezone.utc)
        await self.session.execute(
            update(User).where(User.id == user_id).values(last_login_at=login_time)
        )
        await self.session.flush()

    async def mark_email_verified(self, user_id: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(email_verified=True, is_verified=True)
        )
        await self.session.flush()

    # --- Legacy RefreshToken Support (Backward Compatibility) ---

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
