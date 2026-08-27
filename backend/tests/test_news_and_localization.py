import pytest
from httpx import AsyncClient
from app.services.glossary_service import KazakhLanguageQAService


@pytest.mark.asyncio
async def test_news_articles_and_alerts(client: AsyncClient):
    # 1. Test news listing in Kazakh
    resp_kk = await client.get("/api/v1/news?locale=kk&limit=10")
    assert resp_kk.status_code == 200
    data_kk = resp_kk.json()
    assert data_kk["total"] > 0
    assert len(data_kk["items"]) > 0
    assert data_kk["items"][0]["locale"] == "kk"

    # 2. Test news listing in Russian
    resp_ru = await client.get("/api/v1/news?locale=ru&limit=10")
    assert resp_ru.status_code == 200
    data_ru = resp_ru.json()
    assert data_ru["items"][0]["locale"] == "ru"

    # 3. Test breaking alerts endpoint
    resp_alerts = await client.get("/api/v1/news/alerts?locale=kk")
    assert resp_alerts.status_code == 200
    alerts = resp_alerts.json()
    assert len(alerts) > 0
    assert "2026 жылғы Негізгі ҰБТ" in alerts[0]["title"]

    # 4. Test single news article detail
    first_id = data_kk["items"][0]["id"]
    resp_detail = await client.get(f"/api/v1/news/{first_id}?locale=kk")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert detail["id"] == first_id
    assert "content" in detail
    assert "source_name" in detail


@pytest.mark.asyncio
async def test_localization_glossary_and_qa(client: AsyncClient):
    # 1. Test glossary endpoint
    resp_glossary = await client.get("/api/v1/localization/glossary")
    assert resp_glossary.status_code == 200
    glossary = resp_glossary.json()
    assert len(glossary) >= 30
    keys = [item["concept_key"] for item in glossary]
    assert "unt_full" in keys
    assert "database" in keys

    # 2. Test Kazakh QA validator service
    qa_service = KazakhLanguageQAService()
    
    # Valid natural Kazakh text
    good_text = "Ұлттық бірыңғай тестілеуге дайындық барысында деректер базасы және алгоритмдеу бөлімдерін қайталау маңызды."
    good_res = qa_service.validate_kazakh_text(good_text)
    assert good_res["is_valid"] is True
    assert good_res["quality_score"] >= 0.8

    # Text containing mechanical calque
    calque_text = "Талапкерлер база данных бойынша сұрақтарға жауап беріп, балл жинау қажет."
    calque_res = qa_service.validate_kazakh_text(calque_text)
    assert len(calque_res["warnings"]) > 0

    # API endpoint check
    resp_qa = await client.post("/api/v1/localization/kazakh-qa", json={"text": good_text})
    assert resp_qa.status_code == 200
    assert resp_qa.json()["is_valid"] is True


@pytest.mark.asyncio
async def test_lesson_content_respects_the_requested_locale(client: AsyncClient):
    kk = await client.get("/api/v1/courses/lessons/1?locale=kk")
    en = await client.get("/api/v1/courses/lessons/1?locale=en")
    ru = await client.get("/api/v1/courses/lessons/1?locale=ru")

    assert kk.status_code == en.status_code == ru.status_code == 200
    assert kk.json()["locale"] == "kk"
    assert en.json()["locale"] == "en"
    assert ru.json()["locale"] == "ru"
    assert kk.json()["title"].startswith("Позициялық")
    assert en.json()["title"].startswith("Positional")
    assert ru.json()["title"].startswith("Позиционные")
    assert "```python" in kk.json()["content"]


@pytest.mark.asyncio
async def test_unified_search(client: AsyncClient):
    # Search for Python
    resp = await client.get("/api/v1/search?q=Python&locale=kk")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_matches"] > 0
    assert len(data["results"]) > 0
