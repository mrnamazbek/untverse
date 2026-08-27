from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints import internal_jobs
from app.core.config import settings
from app.models.news import NewsArticle
from app.models.sources import IngestionRun, SourceDocument
from app.services import ntc_news_ingestion
from app.services.ntc_news_ingestion import FetchedNtcListing, NtcNewsItem, parse_ntc_listing


NTC_LISTING_FIXTURE = """
<article class="news-card">
  <a class="news-card__image" href="/?custom_news_section=ignore"><img></a>
  <div class="news-card__content">
    <h3 class="news-card__title">ҰБТ 2026: тіркелу басталды</h3>
    <p class="news-card__excerpt">Ресми <b>ҰТО</b> хабарламасы.</p>
    <a class="news-card__link" href="/?custom_news_section=unt-2026&amp;lang=kk">Толығырақ</a>
    <span class="news-card__meta">21 августа, 2026</span>
  </div>
</article>
<article class="news-card"><h3 class="news-card__title">Missing data</h3></article>
"""


def test_parse_ntc_listing_extracts_real_card_shape_and_canonical_url():
    items = parse_ntc_listing(NTC_LISTING_FIXTURE)

    assert len(items) == 1
    assert items[0].canonical_url == "https://testcenter.kz/?custom_news_section=unt-2026&lang=kk"
    assert items[0].title_kk == "ҰБТ 2026: тіркелу басталды"
    assert items[0].summary_kk == "Ресми ҰТО хабарламасы."
    assert items[0].published_at == datetime(2026, 8, 20, 19, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_daily_ntc_ingestion_is_idempotent_and_records_listing_provenance(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
):
    class FakeNtcClient:
        async def fetch_listing(self):
            return FetchedNtcListing(
                url="https://testcenter.kz/",
                raw_html=NTC_LISTING_FIXTURE,
                items=parse_ntc_listing(NTC_LISTING_FIXTURE),
            )

    # The runner normally creates an application session. Use the isolated test DB instead.
    from conftest import TestSessionLocal
    monkeypatch.setattr(ntc_news_ingestion, "async_session_maker", TestSessionLocal)

    first = await ntc_news_ingestion.run_daily_ntc_news_ingestion(client_factory=FakeNtcClient)
    second = await ntc_news_ingestion.run_daily_ntc_news_ingestion(client_factory=FakeNtcClient)

    assert first["status"] == "success"
    assert first["items_created"] == 1
    assert second["items_skipped"] == 1

    articles = (await db_session.execute(select(NewsArticle))).scalars().all()
    assert len(articles) >= 1
    matching = [a for a in articles if a.canonical_url.endswith("custom_news_section=unt-2026&lang=kk")]
    assert len(matching) == 1
    assert len((await db_session.execute(select(SourceDocument))).scalars().all()) == 2
    runs = (await db_session.execute(select(IngestionRun).where(IngestionRun.job_name == "daily_ntc_news_cron"))).scalars().all()
    assert len(runs) == 2


@pytest.mark.asyncio
async def test_internal_job_requires_secret_and_invokes_runner(client, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "NEWS_INGESTION_SECRET", "test-ingestion-secret")

    async def fake_runner():
        return {"status": "success", "items_created": 2}

    monkeypatch.setattr(internal_jobs, "run_daily_ntc_news_ingestion", fake_runner)

    denied = await client.post("/api/v1/internal/jobs/daily-news-ingest")
    accepted = await client.post(
        "/api/v1/internal/jobs/daily-news-ingest",
        headers={"X-UNT-Ingestion-Key": "test-ingestion-secret"},
    )

    assert denied.status_code == 403
    assert accepted.status_code == 200
    assert accepted.json()["items_created"] == 2

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "DATABASE_URL", "sqlite+aiosqlite:///./unsafe.db")
    rejected_sqlite = await client.post(
        "/api/v1/internal/jobs/daily-news-ingest",
        headers={"X-UNT-Ingestion-Key": "test-ingestion-secret"},
    )
    assert rejected_sqlite.status_code == 503
