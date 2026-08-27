import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sse_ingestion_stream(client: AsyncClient):
    """Test SSE streaming of ingestion progress"""
    resp = await client.get("/api/v1/stream/ingestion/test-run-123")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    
    content = resp.text
    assert "event: start" in content
    assert "event: progress" in content
    assert "event: complete" in content
    assert "test-run-123" in content


@pytest.mark.asyncio
async def test_sse_live_events_stream(client: AsyncClient):
    """Test SSE live student events stream"""
    resp = await client.get("/api/v1/stream/live-events?user_id=1")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    
    content = resp.text
    assert "event: connected" in content
    assert "event: heartbeat" in content


@pytest.mark.asyncio
async def test_jsonl_streaming_export(client: AsyncClient):
    """Test chunked NDJSON / JSON Lines question export"""
    resp = await client.get("/api/v1/stream/export/questions.jsonl?locale=kk")
    assert resp.status_code == 200
    assert "application/x-ndjson" in resp.headers["content-type"]
    assert "attachment; filename=unt_questions_kk.jsonl" in resp.headers["content-disposition"]
    
    lines = [line for line in resp.text.split("\n") if line.strip()]
    assert len(lines) > 0
    # Verify each line is valid JSON with Pydantic serialization
    import json
    first_q = json.loads(lines[0])
    assert "id" in first_q
    assert "text" in first_q
    assert "locale" in first_q
    assert first_q["locale"] == "kk"


@pytest.mark.asyncio
async def test_strict_content_type_enforcement(client: AsyncClient):
    """Test that POST requests with body require valid application/json or reject with 415"""
    # 1. Invalid content-type 'text/plain'
    resp_invalid = await client.post(
        "/api/v1/auth/register",
        content="plain text body",
        headers={"Content-Type": "text/plain"},
    )
    assert resp_invalid.status_code == 415
    assert "Unsupported Media Type" in resp_invalid.json()["detail"]

    # 2. Valid content-type 'application/json' is processed normally (even if invalid data -> 422)
    resp_valid = await client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-email"},
    )
    # Status should be 422 Unprocessable Entity (validation error), NOT 415
    assert resp_valid.status_code == 422
