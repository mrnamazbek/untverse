import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gamification_profile_and_leaderboard(client: AsyncClient):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "student@unt-informatics.kz",
        "password": "student12345"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get gamification profile
    prof_resp = await client.get("/api/v1/gamification/profile", headers=headers)
    assert prof_resp.status_code == 200
    prof = prof_resp.json()
    assert "current_level" in prof
    assert "current_xp" in prof
    assert "streak" in prof
    assert "recent_achievements" in prof
    assert "daily_missions" in prof
    assert len(prof["daily_missions"]) > 0

    # 2. Get leaderboard
    lead_resp = await client.get("/api/v1/gamification/leaderboard")
    assert lead_resp.status_code == 200
    leaderboard = lead_resp.json()
    assert len(leaderboard) >= 2
    # Leaderboard should be ordered by XP descending
    assert leaderboard[0]["total_xp"] >= leaderboard[1]["total_xp"]

    # 3. Get student analytics dashboard
    analytics_resp = await client.get("/api/v1/analytics/dashboard", headers=headers)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert "unt_readiness_score" in analytics
    assert "all_topic_masteries" in analytics
