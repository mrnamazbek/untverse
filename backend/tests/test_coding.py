import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_coding_tasks_and_execution(client: AsyncClient):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "student@unt-informatics.kz",
        "password": "student12345"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List tasks
    tasks_resp = await client.get("/api/v1/coding", headers=headers)
    assert tasks_resp.status_code == 200
    tasks = tasks_resp.json()
    assert len(tasks) > 0
    task_id = tasks[0]["id"]

    # 2. Get task details
    task_detail_resp = await client.get(f"/api/v1/coding/{task_id}", headers=headers)
    assert task_detail_resp.status_code == 200
    task_data = task_detail_resp.json()
    assert task_data["solution_code"] is None  # Check solution is not exposed to student

    # 3. Test submitting correct code (Sum of even numbers)
    valid_code = "a = int(input())\nb = int(input())\nprint(sum(x for x in range(a, b + 1) if x % 2 == 0))\n"
    run_resp = await client.post(f"/api/v1/coding/{task_id}/run", json={"source_code": valid_code}, headers=headers)
    assert run_resp.status_code == 200
    res = run_resp.json()
    assert res["status"] == "accepted"
    assert res["passed_tests"] == res["total_tests"]
    assert res["xp_earned"] > 0

    # 4. Test security check: submitting malicious/forbidden code
    malicious_code = "import os\nos.system('echo hacked')\n"
    sec_run_resp = await client.post(f"/api/v1/coding/{task_id}/run", json={"source_code": malicious_code}, headers=headers)
    assert sec_run_resp.status_code == 200
    sec_res = sec_run_resp.json()
    assert sec_res["status"] == "forbidden_syntax"
    assert "запрещен" in sec_res["error_output"]
