import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_quiz_lifecycle_and_scoring(client: AsyncClient):
    # 1. Login as demo student
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "student@unt-informatics.kz",
        "password": "student12345"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get list of quizzes
    quizzes_resp = await client.get("/api/v1/quizzes", headers=headers)
    assert quizzes_resp.status_code == 200
    quizzes = quizzes_resp.json()
    assert len(quizzes) > 0
    quiz_id = quizzes[0]["id"]

    # 3. Get quiz questions
    quiz_detail_resp = await client.get(f"/api/v1/quizzes/{quiz_id}", headers=headers)
    assert quiz_detail_resp.status_code == 200
    quiz_data = quiz_detail_resp.json()
    assert "questions" in quiz_data
    assert len(quiz_data["questions"]) > 0

    # 4. Submit answers (choose first option for each question)
    answers_to_submit = []
    for q in quiz_data["questions"]:
        opt_id = q["options"][0]["id"] if q["options"] else None
        answers_to_submit.append({
            "question_id": q["id"],
            "selected_option_ids": [opt_id] if opt_id else []
        })

    submit_payload = {
        "time_spent_seconds": 120,
        "answers": answers_to_submit
    }
    submit_resp = await client.post(f"/api/v1/quizzes/{quiz_id}/attempts", json=submit_payload, headers=headers)
    assert submit_resp.status_code == 200
    result = submit_resp.json()
    assert "score" in result
    assert "percentage" in result
    assert "xp_earned" in result
    assert result["xp_earned"] > 0
    assert "answers_review" in result
