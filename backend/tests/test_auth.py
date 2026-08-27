import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Register new user
    register_payload = {
        "email": "new_student@unt.kz",
        "password": "Password123!",
        "display_name": "Данияр Касымов",
        "role": "student"
    }
    reg_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_response.status_code == 201, reg_response.text
    data = reg_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "new_student@unt.kz"
    assert data["display_name"] == "Данияр Касымов"

    # 2. Login with valid credentials
    login_payload = {
        "email": "new_student@unt.kz",
        "password": "Password123!"
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    token = login_data["access_token"]
    assert token is not None

    # 3. Access protected /me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "new_student@unt.kz"
    assert me_data["role"] == "student"

    # 4. Login with invalid password
    bad_login = await client.post("/api/v1/auth/login", json={"email": "new_student@unt.kz", "password": "WrongPassword"})
    assert bad_login.status_code == 401
