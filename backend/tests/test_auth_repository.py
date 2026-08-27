import pytest
from datetime import datetime, timezone, timedelta
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.models.user import UserRoleEnum, Role, UserRole


@pytest.mark.asyncio
async def test_user_repository_auth_accounts_and_sessions(db_session: AsyncSession):
    repo = UserRepository(db_session)

    # 1. Create OAuth user without password
    user = await repo.create_user_with_profile(
        email="google_student@untverse.kz",
        hashed_password=None,
        display_name="Google Student",
        role="student",
        is_verified=True,
        email_verified=True,
    )
    assert user.id is not None
    assert user.email == "google_student@untverse.kz"
    assert user.hashed_password is None
    assert user.email_verified is True
    assert user.profile.display_name == "Google Student"

    # 2. Link Google OAuth account
    google_sub = "google_sub_9876543210"
    account = await repo.link_account(
        user_id=user.id,
        provider="google",
        provider_account_id=google_sub,
        provider_email="google_student@untverse.kz",
    )
    assert account.id is not None
    assert account.provider == "google"
    assert account.provider_account_id == google_sub
    assert account.user_id == user.id

    # 3. Retrieve account by provider
    retrieved_acc = await repo.get_by_provider("google", google_sub)
    assert retrieved_acc is not None
    assert retrieved_acc.user_id == user.id
    assert retrieved_acc.user.email == "google_student@untverse.kz"
    assert retrieved_acc.user.profile.display_name == "Google Student"

    # 4. List user auth accounts
    accounts = await repo.get_auth_accounts_by_user_id(user.id)
    assert len(accounts) == 1
    assert accounts[0].provider == "google"

    # 5. Save and manage refresh sessions (SHA-256 hex)
    raw_token = "mock_secure_refresh_token_string_abc123"
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    session = await repo.save_refresh_session(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        ip_address="127.0.0.1",
    )
    assert session.id is not None
    assert session.token_hash == token_hash
    assert session.revoked is False

    # 6. Retrieve session by hash
    retrieved_session = await repo.get_session_by_hash(token_hash)
    assert retrieved_session is not None
    assert retrieved_session.user_id == user.id
    assert retrieved_session.user_agent == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

    # 7. Rotate & revoke session
    new_raw_token = "mock_secure_refresh_token_string_def456"
    new_token_hash = hashlib.sha256(new_raw_token.encode("utf-8")).hexdigest()

    revoked = await repo.revoke_session_by_hash(token_hash, replaced_by_hash=new_token_hash)
    assert revoked is True

    # Verify session is now marked revoked
    updated_session = await repo.get_session_by_hash(token_hash)
    assert updated_session.revoked is True
    assert updated_session.replaced_by_hash == new_token_hash
    assert updated_session.revoked_at is not None

    # 8. Create another active session and test revoke_all_user_sessions
    await repo.save_refresh_session(
        user_id=user.id,
        token_hash=new_token_hash,
        expires_at=expires_at,
        user_agent="Mobile App",
        ip_address="192.168.1.50",
    )
    active_revoked_count = await repo.revoke_all_user_sessions(user.id)
    assert active_revoked_count == 1

    revoked_new_session = await repo.get_session_by_hash(new_token_hash)
    assert revoked_new_session.revoked is True

    # 9. Update last login
    now_login = datetime.now(timezone.utc)
    await repo.update_last_login(user.id, now_login)
    reloaded_user = await repo.get_with_profile(user.id)
    assert reloaded_user.last_login_at is not None

    # 10. Test unlinking provider
    unlinked = await repo.unlink_account(user.id, "google")
    assert unlinked is True
    accounts_after = await repo.get_auth_accounts_by_user_id(user.id)
    assert len(accounts_after) == 0


@pytest.mark.asyncio
async def test_roles_and_user_roles_relationships(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.create_user_with_profile(
        email="moderator_candidate@untverse.kz",
        hashed_password="hashed_pwd_123",
        display_name="Модератор Кандидат",
        role="moderator",
    )
    assert user.role == "moderator"
    reloaded_user = await repo.get_with_profile(user.id)
    assert len(reloaded_user.user_roles) >= 1
    assert reloaded_user.user_roles[0].role.name == "moderator"
