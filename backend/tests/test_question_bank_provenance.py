import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.question_bank_service import QuestionBankService
from app.services.question_selection_service import QuestionSelectionService


@pytest.mark.asyncio
async def test_question_bank_listing_and_filtering(client: AsyncClient, db_session: AsyncSession):
    # 1. Test listing with default Kazakh locale
    resp_kk = await client.get("/api/v1/questions?locale=kk&limit=10")
    assert resp_kk.status_code == 200
    data_kk = resp_kk.json()
    assert "items" in data_kk
    assert data_kk["total"] > 0
    first_item = data_kk["items"][0]
    assert first_item["locale"] == "kk"
    assert len(first_item["options"]) > 0
    assert len(first_item["provenance"]) > 0
    assert "source_title" in first_item["provenance"][0]

    # 2. Test listing with Russian locale
    resp_ru = await client.get("/api/v1/questions?locale=ru&limit=10")
    assert resp_ru.status_code == 200
    data_ru = resp_ru.json()
    assert data_ru["items"][0]["locale"] == "ru"

    # 3. Test filtering by difficulty
    resp_diff = await client.get("/api/v1/questions?difficulty=A")
    assert resp_diff.status_code == 200
    for item in resp_diff.json()["items"]:
        assert item["difficulty"] == "A"


@pytest.mark.asyncio
async def test_question_detail_and_provenance(client: AsyncClient, db_session: AsyncSession):
    # Fetch questions list to get ID
    list_res = await client.get("/api/v1/questions?limit=1")
    items = list_res.json()["items"]
    assert len(items) > 0
    q_id = items[0]["id"]

    # Fetch detail
    detail_res = await client.get(f"/api/v1/questions/{q_id}?locale=kk")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == q_id
    assert "solutions" in detail
    assert len(detail["solutions"]) > 0
    assert "step_by_step_explanation" in detail["solutions"][0]
    assert "exam_tip" in detail["solutions"][0]
    assert len(detail["provenance"]) > 0
    assert detail["provenance"][0]["official_status"] is not None


@pytest.mark.asyncio
async def test_question_selection_and_unt_mock(db_session: AsyncSession):
    selection_service = QuestionSelectionService(db_session)

    # 1. Test sampling by topic
    sample = await selection_service.sample_by_topic(specification_topic_id=1, count=5, locale="kk")
    assert isinstance(sample, list)

    # 2. Test 50 mock generator
    mock_questions = await selection_service.generate_unt_50_mock(locale="kk")
    assert len(mock_questions) > 0
    for mq in mock_questions:
        assert "options" in mq
        assert "provenance" in mq
