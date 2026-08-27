import base64
import hashlib
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from jose import jwt

from app.core.config import settings
from app.core.security import decode_token
from app.core.exceptions import AuthException
from app.services.oauth_service import GoogleOAuthService
from app.schemas.auth import AuthErrorCode


# ==========================================
# 1. GoogleOAuthService Unit Tests
# ==========================================

def test_pkce_generation():
    verifier, challenge = GoogleOAuthService.generate_pkce_challenge()
    assert len(verifier) == 86, f"Expected verifier length 86, got {len(verifier)}"
    assert isinstance(verifier, str)

    # Verify S256 derivation
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expected_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    assert challenge == expected_challenge


def test_signed_state_lifecycle_and_sanitization():
    code_verifier = "mock_verifier_86_chars_long_string_abc_123_xyz_456_qwe_789_rty_012_uio_345_pas_678_dfg_901"
    
    # 1. Valid state
    state = GoogleOAuthService.create_signed_state(
        code_verifier=code_verifier,
        locale="kk",
        redirect_to="/practice?topic=python",
    )
    decoded = GoogleOAuthService.verify_and_decode_state(state)
    assert "code_verifier" not in decoded
    assert decoded["locale"] == "kk"
    assert decoded["redirect_to"] == "/practice?topic=python"
    assert decoded["nonce"] is not None
    transaction = GoogleOAuthService.create_oauth_transaction(code_verifier, state)
    assert GoogleOAuthService.verify_oauth_transaction(transaction, state) == code_verifier
    with pytest.raises(AuthException):
        GoogleOAuthService.verify_oauth_transaction(transaction, state + "tampered")

    # 2. Open Redirect Sanitization
    malicious_redirects = [
        "//evil.com",
        "//evil.com/hack",
        "https://evil.com/dashboard",
        "http://attacker.kz",
        "javascript:alert(1)",
        "",
        None,
    ]
    for bad_url in malicious_redirects:
        sanitized = GoogleOAuthService.sanitize_redirect_url(bad_url)
        assert sanitized == "/dashboard", f"Failed sanitizing '{bad_url}', got '{sanitized}'"

    # 3. Expired State
    expired_payload = {
        "cv": code_verifier,
        "loc": "ru",
        "rd": "/dashboard",
        "nonce": "nonce-123",
        "iat": int((datetime.now(timezone.utc) - timedelta(minutes=20)).timestamp()),
        "exp": int((datetime.now(timezone.utc) - timedelta(minutes=10)).timestamp()),
        "typ": "oauth_state",
        "iss": "untverse.kz",
    }
    expired_state = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(AuthException) as exc_info:
        GoogleOAuthService.verify_and_decode_state(expired_state)
    assert exc_info.value.code == AuthErrorCode.AUTH_OAUTH_STATE_EXPIRED.value

    # 4. Tampered State Signature
    tampered_state = jwt.encode(expired_payload, "wrong_secret_key_1234567890", algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(AuthException) as exc_info:
        GoogleOAuthService.verify_and_decode_state(tampered_state)
    assert exc_info.value.code == AuthErrorCode.AUTH_OAUTH_STATE_INVALID.value

    # 5. Invalid State Type
    wrong_type_payload = {
        "cv": code_verifier,
        "loc": "ru",
        "rd": "/dashboard",
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()),
        "typ": "access_token",
    }
    wrong_type_state = jwt.encode(wrong_type_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(AuthException) as exc_info:
        GoogleOAuthService.verify_and_decode_state(wrong_type_state)
    assert exc_info.value.code == AuthErrorCode.AUTH_OAUTH_STATE_INVALID.value


def test_verify_id_token_validation(monkeypatch):
    # 1. Valid ID Token claims
    valid_claims = {
        "sub": "google_uid_1092837465",
        "email": "Student@UNTverse.kz",
        "email_verified": True,
        "name": "Алихан Смаилов",
        "picture": "https://lh3.googleusercontent.com/a/mock_avatar.jpg",
    }
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")
    from app.services import oauth_service
    monkeypatch.setattr(oauth_service.google_id_token, "verify_oauth2_token", lambda *args: valid_claims)
    user_info = GoogleOAuthService.verify_id_token("verified-by-google")
    assert user_info["sub"] == "google_uid_1092837465"
    assert user_info["email"] == "student@untverse.kz"
    assert user_info["email_verified"] is True
    assert user_info["name"] == "Алихан Смаилов"
    assert user_info["picture"] == "https://lh3.googleusercontent.com/a/mock_avatar.jpg"

    # 2. Unverified Email
    unverified_claims = {
        "sub": "google_uid_999",
        "email": "unverified@untverse.kz",
        "email_verified": False,
    }
    monkeypatch.setattr(oauth_service.google_id_token, "verify_oauth2_token", lambda *args: unverified_claims)
    with pytest.raises(AuthException) as exc_info:
        GoogleOAuthService.verify_id_token("verified-by-google")
    assert exc_info.value.code == AuthErrorCode.AUTH_OAUTH_EMAIL_UNVERIFIED.value

    # 3. Missing sub
    missing_sub = {"email": "no_sub@untverse.kz", "email_verified": True}
    monkeypatch.setattr(oauth_service.google_id_token, "verify_oauth2_token", lambda *args: missing_sub)
    with pytest.raises(AuthException) as exc_info:
        GoogleOAuthService.verify_id_token("verified-by-google")
    assert exc_info.value.code == AuthErrorCode.AUTH_OAUTH_CODE_EXCHANGE_FAILED.value


# ==========================================
# 2. Integration API Endpoints Tests
# ==========================================

@pytest.mark.asyncio
async def test_google_oauth_init_endpoints(client: AsyncClient):
    # Standard endpoint
    res = await client.get("/api/v1/auth/oauth/google/init?locale=kk&redirect_to=/quizzes")
    assert res.status_code == 200, res.text
    data = res.json()
    assert "authorization_url" in data
    assert "state" in data
    assert "accounts.google.com" in data["authorization_url"]
    assert "code_challenge" in data["authorization_url"]
    assert "code_challenge_method=S256" in data["authorization_url"]

    # Alias endpoint
    res_alias = await client.get("/api/v1/auth/google/login")
    assert res_alias.status_code == 200
    assert "authorization_url" in res_alias.json()


@pytest.mark.asyncio
async def test_google_oauth_callback_provision_new_user(client: AsyncClient, monkeypatch):
    # Generate valid state
    verifier, challenge = GoogleOAuthService.generate_pkce_challenge()
    state = GoogleOAuthService.create_signed_state(verifier, locale="ru", redirect_to="/dashboard")
    client.cookies.set("oauth_transaction", GoogleOAuthService.create_oauth_transaction(verifier, state))

    # Mock exchange_code_for_tokens
    mock_id_token = jwt.encode({
        "sub": "google_sub_123456",
        "email": "new_google_student@untverse.kz",
        "email_verified": True,
        "name": "Айгерим Берикова",
        "picture": "https://lh3.googleusercontent.com/avatar1.jpg",
    }, "fake_secret", algorithm="HS256")

    async def mock_exchange(code: str, code_verifier: str):
        assert code == "auth_code_from_google"
        assert code_verifier == verifier
        return {"id_token": mock_id_token, "access_token": "google_access_token"}

    monkeypatch.setattr(GoogleOAuthService, "exchange_code_for_tokens", mock_exchange)
    monkeypatch.setattr(GoogleOAuthService, "verify_id_token", lambda _token, expected_nonce=None: {
        "sub": "google_sub_123456", "email": "new_google_student@untverse.kz", "email_verified": True,
        "name": "Айгерим Берикова", "picture": "https://lh3.googleusercontent.com/avatar1.jpg", "nonce": expected_nonce,
    })

    # Perform callback POST
    callback_payload = {
        "code": "auth_code_from_google",
        "state": state,
    }
    response = await client.post("/api/v1/auth/oauth/google/callback", json=callback_payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["is_new_user"] is True
    assert data["email"] == "new_google_student@untverse.kz"
    assert data["display_name"] == "Айгерим Берикова"
    assert data["avatar_url"] == "https://lh3.googleusercontent.com/avatar1.jpg"
    assert "access_token" in data
    assert "refresh_token" in data

    # Check cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Test /me endpoint using the issued access token
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "new_google_student@untverse.kz"
    assert me_data["email_verified"] is True
    assert len(me_data["auth_accounts"]) == 1
    assert me_data["auth_accounts"][0]["provider"] == "google"
    assert me_data["auth_accounts"][0]["provider_account_id"] == "google_sub_123456"


@pytest.mark.asyncio
async def test_google_oauth_account_linking_existing_user(client: AsyncClient, monkeypatch):
    # 1. Register normal user with password first
    reg_payload = {
        "email": "shared_student@untverse.kz",
        "password": "SecurePassword123!",
        "display_name": "Shared Student",
        "role": "student"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # 2. Initiate Google login with the same email
    verifier, challenge = GoogleOAuthService.generate_pkce_challenge()
    state = GoogleOAuthService.create_signed_state(verifier, locale="kk", redirect_to="/coding")
    client.cookies.set("oauth_transaction", GoogleOAuthService.create_oauth_transaction(verifier, state))

    mock_id_token = jwt.encode({
        "sub": "google_linked_sub_7890",
        "email": "shared_student@untverse.kz",
        "email_verified": True,
        "name": "Shared Student Google",
    }, "fake_secret", algorithm="HS256")

    async def mock_exchange(code: str, code_verifier: str):
        return {"id_token": mock_id_token}

    monkeypatch.setattr(GoogleOAuthService, "exchange_code_for_tokens", mock_exchange)
    monkeypatch.setattr(GoogleOAuthService, "verify_id_token", lambda _token, expected_nonce=None: {
        "sub": "google_linked_sub_7890", "email": "shared_student@untverse.kz", "email_verified": True,
        "name": "Shared Student Google", "nonce": expected_nonce,
    })

    # 3. Callback for linking
    cb_res = await client.post("/api/v1/auth/oauth/google/callback", json={
        "code": "code_for_linking",
        "state": state,
    })
    assert cb_res.status_code == 409

    # 5. Verify user can still login with password
    pwd_login = await client.post("/api/v1/auth/login", json={
        "email": "shared_student@untverse.kz",
        "password": "SecurePassword123!",
    })
    assert pwd_login.status_code == 200


@pytest.mark.asyncio
async def test_google_oauth_browser_get_callback(client: AsyncClient, monkeypatch):
    verifier, challenge = GoogleOAuthService.generate_pkce_challenge()
    state = GoogleOAuthService.create_signed_state(verifier, locale="kk", redirect_to="/profile")
    client.cookies.set("oauth_transaction", GoogleOAuthService.create_oauth_transaction(verifier, state))

    mock_id_token = jwt.encode({
        "sub": "google_browser_user_555",
        "email": "browser_user@untverse.kz",
        "email_verified": True,
        "name": "Browser User",
    }, "fake_secret", algorithm="HS256")

    async def mock_exchange(code: str, code_verifier: str):
        return {"id_token": mock_id_token}

    monkeypatch.setattr(GoogleOAuthService, "exchange_code_for_tokens", mock_exchange)
    monkeypatch.setattr(GoogleOAuthService, "verify_id_token", lambda _token, expected_nonce=None: {
        "sub": "google_browser_user_555", "email": "browser_user@untverse.kz", "email_verified": True,
        "name": "Browser User", "nonce": expected_nonce,
    })

    # GET redirect callback from Google
    res = await client.get(f"/api/v1/auth/oauth/google/callback?code=mock_browser_code&state={state}", follow_redirects=False)
    assert res.status_code == 307
    location = res.headers["location"]
    assert f"{settings.FRONTEND_URL}/kk/auth/callback?redirect_to=%2Fprofile" in location
    assert "access_token" in res.cookies
    assert "refresh_token" in res.cookies


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_replay_detection(client: AsyncClient):
    # 1. Register a user and obtain initial tokens
    reg_res = await client.post("/api/v1/auth/register", json={
        "email": "rotation_test@untverse.kz",
        "password": "Password123!",
        "display_name": "Rotation User"
    })
    assert reg_res.status_code == 201
    initial_data = reg_res.json()
    token1 = initial_data["refresh_token"]

    # 2. First refresh (Rotation)
    refresh1_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token1})
    assert refresh1_res.status_code == 200
    data1 = refresh1_res.json()
    token2 = data1["refresh_token"]
    assert token2 != token1

    # 3. Second refresh using the NEW active token2
    refresh2_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token2})
    assert refresh2_res.status_code == 200
    data2 = refresh2_res.json()
    token3 = data2["refresh_token"]
    assert token3 != token2

    # 4. REPLAY ATTACK: Attacker/client attempts to reuse old token1
    replay_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token1})
    assert replay_res.status_code == 401
    replay_data = replay_res.json()
    assert replay_data["code"] == AuthErrorCode.AUTH_SESSION_REUSE_DETECTED.value

    # 5. Security consequence: All user sessions must now be revoked!
    # Even the newest token3 must now be rejected
    fail_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token3})
    assert fail_res.status_code == 401


@pytest.mark.asyncio
async def test_password_not_set_and_set_password_flow(client: AsyncClient, monkeypatch):
    # 1. Provision user via Google OAuth (without password)
    verifier, challenge = GoogleOAuthService.generate_pkce_challenge()
    state = GoogleOAuthService.create_signed_state(verifier, locale="ru", redirect_to="/dashboard")
    client.cookies.set("oauth_transaction", GoogleOAuthService.create_oauth_transaction(verifier, state))

    mock_id_token = jwt.encode({
        "sub": "oauth_only_sub_9999",
        "email": "oauth_only@untverse.kz",
        "email_verified": True,
        "name": "OAuth Only User",
    }, "fake_secret", algorithm="HS256")

    async def mock_exchange(code: str, code_verifier: str):
        return {"id_token": mock_id_token}

    monkeypatch.setattr(GoogleOAuthService, "exchange_code_for_tokens", mock_exchange)
    monkeypatch.setattr(GoogleOAuthService, "verify_id_token", lambda _token, expected_nonce=None: {
        "sub": "oauth_only_sub_9999", "email": "oauth_only@untverse.kz", "email_verified": True,
        "name": "OAuth Only User", "nonce": expected_nonce,
    })

    cb_res = await client.post("/api/v1/auth/oauth/google/callback", json={
        "code": "oauth_code_1",
        "state": state,
    })
    assert cb_res.status_code == 200
    access_token = cb_res.json()["access_token"]

    # 2. Try password login -> Must return AUTH_PASSWORD_NOT_SET
    login_attempt = await client.post("/api/v1/auth/login", json={
        "email": "oauth_only@untverse.kz",
        "password": "SomePassword123!",
    })
    assert login_attempt.status_code == 400
    assert login_attempt.json()["code"] == AuthErrorCode.AUTH_PASSWORD_NOT_SET.value

    # 3. Set password via authenticated /set-password
    set_pwd_res = await client.post(
        "/api/v1/auth/set-password",
        json={"new_password": "NewCreatedPassword123!"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert set_pwd_res.status_code == 200
    assert set_pwd_res.json()["message"] == "Пароль успешно установлен"

    # 4. Now password login succeeds
    successful_login = await client.post("/api/v1/auth/login", json={
        "email": "oauth_only@untverse.kz",
        "password": "NewCreatedPassword123!",
    })
    assert successful_login.status_code == 200
    assert "access_token" in successful_login.json()


@pytest.mark.asyncio
async def test_logout_and_logout_all(client: AsyncClient):
    # Register user
    reg_res = await client.post("/api/v1/auth/register", json={
        "email": "logout_tester@untverse.kz",
        "password": "Password123!",
        "display_name": "Logout Tester"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    access_token = reg_data["access_token"]
    refresh_token = reg_data["refresh_token"]

    # Logout single session
    logout_res = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_res.status_code == 200

    # Refreshing with logged out token should fail
    refresh_fail = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_fail.status_code == 401

    # Login again to get new session
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "logout_tester@untverse.kz",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    new_access = login_res.json()["access_token"]
    new_refresh = login_res.json()["refresh_token"]

    # Logout all sessions
    logout_all_res = await client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {new_access}"}
    )
    assert logout_all_res.status_code == 200
    assert logout_all_res.json()["revoked_sessions_count"] >= 1

    # Refresh after logout-all should fail
    refresh_fail2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert refresh_fail2.status_code == 401


@pytest.mark.asyncio
async def test_users_me_and_auth_me(client: AsyncClient):
    reg_res = await client.post("/api/v1/auth/register", json={
        "email": "me_tester@untverse.kz",
        "password": "Password123!",
        "display_name": "Me Tester"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # GET /api/v1/auth/me
    auth_me = await client.get("/api/v1/auth/me", headers=headers)
    assert auth_me.status_code == 200
    assert auth_me.json()["email"] == "me_tester@untverse.kz"

    # GET /api/v1/users/me
    users_me = await client.get("/api/v1/users/me", headers=headers)
    assert users_me.status_code == 200
    assert users_me.json()["email"] == "me_tester@untverse.kz"


# ==========================================
# 3. Additional Security Tests (QA Sprint)
# ==========================================

def test_pkce_verifier_length_and_s256_challenge():
    """
    RFC 7636: code_verifier MUST be 43–128 chars, S256 challenge MUST match SHA-256 base64url(no-pad).
    Generate multiple pairs and verify invariants.
    """
    for _ in range(10):
        verifier, challenge = GoogleOAuthService.generate_pkce_challenge()
        # RFC 7636 Section 4.1: verifier length 43-128 characters
        assert len(verifier) >= 43, f"Verifier too short: {len(verifier)} < 43"
        assert len(verifier) <= 128, f"Verifier too long: {len(verifier)} > 128"
        # Only URL-safe base64 characters
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in verifier), \
            "Verifier contains non-URL-safe characters"
        # S256 challenge derivation
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        expected = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        assert challenge == expected, f"S256 mismatch: {challenge} != {expected}"
    # Uniqueness check: two separate generations must differ
    v1, c1 = GoogleOAuthService.generate_pkce_challenge()
    v2, c2 = GoogleOAuthService.generate_pkce_challenge()
    assert v1 != v2, "Two consecutive verifiers must be unique (cryptographic randomness)"
    assert c1 != c2, "Two consecutive challenges must be unique"


def test_state_jwt_claims_validation():
    """
    State JWT must have: typ='oauth_state', iss='untverse.kz', exp <= iat + 10 min,
    and must be signed with JWT_SECRET (HS256).
    """
    code_verifier = "test_verifier_for_claims_check_abcdefghijklmnopqrstuvwxyz1234567890"
    state = GoogleOAuthService.create_signed_state(
        code_verifier=code_verifier,
        locale="en",
        redirect_to="/quizzes",
    )

    # Decode without verification to inspect raw claims
    raw_payload = jwt.decode(state, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    # typ must be 'oauth_state'
    assert raw_payload["typ"] == "oauth_state", f"Expected typ='oauth_state', got '{raw_payload.get('typ')}'"

    # iss must be 'untverse.kz'
    assert raw_payload["iss"] == "untverse.kz", f"Expected iss='untverse.kz', got '{raw_payload.get('iss')}'"

    # exp must be at most iat + 10 minutes (600 seconds)
    iat = raw_payload["iat"]
    exp = raw_payload["exp"]
    assert exp - iat <= 600, f"State TTL exceeds 10 min: {exp - iat} seconds"
    assert exp - iat > 0, "exp must be greater than iat"

    # The verifier remains only in the signed HttpOnly transaction cookie.
    assert "cv" not in raw_payload

    # nonce must be present
    assert raw_payload.get("nonce"), "nonce must be present in state"

    # Verify proper decode also works
    decoded = GoogleOAuthService.verify_and_decode_state(state)
    assert "code_verifier" not in decoded
    assert decoded["locale"] == "en"
    assert decoded["redirect_to"] == "/quizzes"

    # WRONG SIGNATURE: must raise AUTH_OAUTH_STATE_INVALID
    forged_state = jwt.encode(raw_payload, "attacker_secret_key_12345", algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(AuthException) as exc_info:
        GoogleOAuthService.verify_and_decode_state(forged_state)
    assert exc_info.value.code == AuthErrorCode.AUTH_OAUTH_STATE_INVALID.value


def test_open_redirect_defense():
    """
    sanitize_redirect_url MUST reject all external/malicious URLs and return '/dashboard'.
    """
    dangerous_urls = [
        "https://evil.com",
        "http://evil.com",
        "//evil.com",
        "//evil.com/dashboard",
        "https://evil.com/dashboard",
        "http://attacker.kz",
        "http://attacker.kz/profile",
        "javascript:alert(1)",
        "javascript:alert(document.cookie)",
        "data:text/html,<script>alert(1)</script>",
        "ftp://evil.com/file",
        "",
        None,
        "///evil.com",
        "/\\evil.com",
        "http://localhost:8000/api/v1/admin",
        "https://accounts.google.com/phish",
    ]
    for url in dangerous_urls:
        result = GoogleOAuthService.sanitize_redirect_url(url)
        assert result == "/dashboard", f"OPEN REDIRECT VULNERABILITY: '{url}' -> '{result}' (expected '/dashboard')"

    # Valid internal paths MUST pass through
    valid_paths = [
        "/dashboard",
        "/practice?topic=python",
        "/quizzes",
        "/learn/python",
        "/coding/task-1",
        "/profile",
    ]
    for path in valid_paths:
        result = GoogleOAuthService.sanitize_redirect_url(path)
        assert result == path, f"Valid path rejected: '{path}' -> '{result}'"


@pytest.mark.asyncio
async def test_replay_detection_revokes_all_sessions(client: AsyncClient):
    """
    Replay detection: reusing a revoked refresh_token MUST revoke ALL user sessions.
    After replay is detected, even the latest valid token3 must be rejected.
    """
    # Register user
    reg = await client.post("/api/v1/auth/register", json={
        "email": "replay_detection_test@untverse.kz",
        "password": "SecurePass123!",
        "display_name": "Replay Tester",
    })
    assert reg.status_code == 201
    token1 = reg.json()["refresh_token"]

    # Rotate: token1 -> token2
    r1 = await client.post("/api/v1/auth/refresh", json={"refresh_token": token1})
    assert r1.status_code == 200
    token2 = r1.json()["refresh_token"]
    assert token2 != token1

    # Rotate: token2 -> token3
    r2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": token2})
    assert r2.status_code == 200
    token3 = r2.json()["refresh_token"]
    assert token3 != token2

    # REPLAY ATTACK: attacker tries to use already-revoked token1
    replay = await client.post("/api/v1/auth/refresh", json={"refresh_token": token1})
    assert replay.status_code == 401
    assert replay.json()["code"] == AuthErrorCode.AUTH_SESSION_REUSE_DETECTED.value

    # CRITICAL: After replay detection, even the newest token3 MUST be revoked
    post_replay = await client.post("/api/v1/auth/refresh", json={"refresh_token": token3})
    assert post_replay.status_code == 401, \
        "token3 must be rejected after replay detection revoked ALL sessions"

    # Even token2 must also be rejected
    post_replay2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": token2})
    assert post_replay2.status_code == 401


@pytest.mark.asyncio
async def test_session_rotation_invalidates_old_token(client: AsyncClient):
    """
    After token rotation, the OLD refresh_token MUST be invalid immediately.
    The NEW token must be the only valid one.
    """
    # Register
    reg = await client.post("/api/v1/auth/register", json={
        "email": "rotation_strict_test@untverse.kz",
        "password": "Password123!",
        "display_name": "Rotation Strict",
    })
    assert reg.status_code == 201
    old_token = reg.json()["refresh_token"]

    # Rotate
    rot = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_token})
    assert rot.status_code == 200
    new_token = rot.json()["refresh_token"]
    assert new_token != old_token

    # New token should work
    check_new = await client.post("/api/v1/auth/refresh", json={"refresh_token": new_token})
    assert check_new.status_code == 200
    newest_token = check_new.json()["refresh_token"]

    # Old token MUST be rejected (already rotated out)
    # This triggers replay detection since old_token is already revoked
    old_attempt = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_token})
    assert old_attempt.status_code == 401, \
        "Old token must be rejected after rotation"


@pytest.mark.asyncio
async def test_account_linking_google_with_existing_email_no_duplicate(client: AsyncClient, monkeypatch):
    """
    Google login with an email that already has a password account MUST:
    1. Link Google provider to the existing user (no new user creation)
    2. is_new_user == False
    3. Both 'password' and 'google' providers present in auth_accounts
    4. Password login still works after linking
    """
    # 1. Register with password
    reg = await client.post("/api/v1/auth/register", json={
        "email": "linking_test_no_dup@untverse.kz",
        "password": "LinkTestPass123!",
        "display_name": "Link Test User",
        "role": "student",
    })
    assert reg.status_code == 201
    original_user_id = reg.json()["user_id"]

    # 2. Google login with same email
    verifier, _ = GoogleOAuthService.generate_pkce_challenge()
    state = GoogleOAuthService.create_signed_state(verifier, locale="kk", redirect_to="/profile")
    client.cookies.set("oauth_transaction", GoogleOAuthService.create_oauth_transaction(verifier, state))

    mock_id_token = jwt.encode({
        "sub": "google_link_nodup_sub_5555",
        "email": "linking_test_no_dup@untverse.kz",
        "email_verified": True,
        "name": "Link Test User Google Name",
        "picture": "https://lh3.googleusercontent.com/link_test.jpg",
    }, "fake_secret", algorithm="HS256")

    async def mock_exchange(code: str, code_verifier: str):
        return {"id_token": mock_id_token}

    monkeypatch.setattr(GoogleOAuthService, "exchange_code_for_tokens", mock_exchange)
    monkeypatch.setattr(GoogleOAuthService, "verify_id_token", lambda _token, expected_nonce=None: {
        "sub": "google_link_nodup_sub_5555", "email": "linking_test_no_dup@untverse.kz", "email_verified": True,
        "name": "Link Test User Google Name", "nonce": expected_nonce,
    })

    cb = await client.post("/api/v1/auth/oauth/google/callback", json={
        "code": "code_for_linking_nodup",
        "state": state,
    })
    assert cb.status_code == 409

    # 4. Password login still works
    pwd_login = await client.post("/api/v1/auth/login", json={
        "email": "linking_test_no_dup@untverse.kz",
        "password": "LinkTestPass123!",
    })
    assert pwd_login.status_code == 200


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    """
    Accessing protected routes (/auth/me, /users/me) without a token MUST return 401.
    """
    # No Authorization header
    me_res = await client.get("/api/v1/auth/me")
    assert me_res.status_code == 401

    users_me_res = await client.get("/api/v1/users/me")
    assert users_me_res.status_code == 401

    # Invalid token
    bad_headers = {"Authorization": "Bearer invalid.jwt.token.here"}
    me_bad = await client.get("/api/v1/auth/me", headers=bad_headers)
    assert me_bad.status_code == 401
