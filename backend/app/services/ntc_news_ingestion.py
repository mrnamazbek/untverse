"""Fetch and ingest the public news feed published by Kazakhstan's NTC.

This module deliberately keeps the source-specific HTML parsing isolated from the
database writer.  The NTC site is a WordPress site and does not expose a stable
public API for this news type, so the parser only relies on its public
``news-card`` markup and fails closed when a card is incomplete.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Callable, Optional
from urllib.parse import urldefrag, urljoin
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.sources import (
    IngestionRun,
    IngestionRunStatus,
    Source,
    SourceDocument,
)
from app.services.ingestion_service import IngestionEngine

logger = logging.getLogger(__name__)

# The public home page currently exposes the NTC's news cards server-side. The
# nominal archive page is not consistently populated by the upstream WordPress
# theme, so using it would silently ingest nothing.
NTC_NEWS_LISTING_URL = "https://testcenter.kz/"
MAX_RESPONSE_BYTES = 2_000_000
MAX_ITEMS_PER_RUN = 30
_KZ_TZ = ZoneInfo("Asia/Almaty")


@dataclass(frozen=True)
class NtcNewsItem:
    canonical_url: str
    title_kk: str
    summary_kk: str
    published_at: Optional[datetime]


@dataclass(frozen=True)
class FetchedNtcListing:
    url: str
    raw_html: str
    items: list[NtcNewsItem]


@dataclass
class _Card:
    href: str = ""
    title: str = ""
    excerpt: str = ""
    date: str = ""


class _NtcNewsCardParser(HTMLParser):
    """Minimal parser for public NTC news cards, without executing page JS."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[_Card] = []
        self._card: Optional[_Card] = None
        self._card_depth = 0
        self._field: Optional[str] = None
        self._field_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "article" and "news-card" in classes and self._card is None:
            self._card = _Card()
            self._card_depth = 1
            return
        if self._card is None:
            return

        # HTMLParser does not synthesize end tags for void HTML elements. Counting
        # them would leave every real NTC card open because its image is an <img>.
        is_void = tag in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        if not is_void:
            self._card_depth += 1
        if tag == "a" and attributes.get("href") and (
            "news-card__link" in classes or not self._card.href
        ):
            self._card.href = attributes["href"] or ""
        if tag == "h3" and "news-card__title" in classes:
            self._field, self._field_depth = "title", 1
        elif tag == "p" and "news-card__excerpt" in classes:
            self._field, self._field_depth = "excerpt", 1
        elif tag in {"span", "time"} and "news-card__meta" in classes:
            self._field, self._field_depth = "date", 1
        elif self._field and not is_void:
            self._field_depth += 1

    def handle_data(self, data: str) -> None:
        if self._card is not None and self._field and data.strip():
            current = getattr(self._card, self._field)
            setattr(self._card, self._field, f"{current} {data.strip()}".strip())

    def handle_endtag(self, tag: str) -> None:
        if self._card is None:
            return
        if self._field:
            self._field_depth -= 1
            if self._field_depth == 0:
                self._field = None
        self._card_depth -= 1
        if self._card_depth == 0:
            self.cards.append(self._card)
            self._card = None


_MONTHS = {
    "қаңтар": 1, "январь": 1, "января": 1,
    "февраль": 2, "февраля": 2, "ақпан": 2,
    "март": 3, "марта": 3, "наурыз": 3,
    "апрель": 4, "апреля": 4, "сәуір": 4,
    "май": 5, "мая": 5,
    "июнь": 6, "июня": 6, "маусым": 6,
    "июль": 7, "июля": 7, "шілде": 7,
    "август": 8, "августа": 8, "тамыз": 8,
    "сентябрь": 9, "сентября": 9, "қыркүйек": 9,
    "октябрь": 10, "октября": 10, "қазан": 10,
    "ноябрь": 11, "ноября": 11, "қараша": 11,
    "декабрь": 12, "декабря": 12, "желтоқсан": 12,
}


def _parse_ntc_date(value: str) -> Optional[datetime]:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    match = re.search(r"(\d{1,2})\s+([а-яё]+),?\s+(\d{4})", normalized)
    if not match:
        match = re.search(r"(\d{4})\s*жылғы\s*(\d{1,2})\s+([а-яё]+)", normalized)
        if not match:
            return None
        year, day, month_name = match.groups()
    else:
        day, month_name, year = match.groups()
    month = _MONTHS.get(month_name)
    if not month:
        return None
    try:
        return datetime(int(year), month, int(day), tzinfo=_KZ_TZ).astimezone(timezone.utc)
    except ValueError:
        return None


def parse_ntc_listing(html: str, listing_url: str = NTC_NEWS_LISTING_URL) -> list[NtcNewsItem]:
    """Extract public NTC news cards into canonical, provenance-safe records."""
    parser = _NtcNewsCardParser()
    parser.feed(html)
    parser.close()

    items: list[NtcNewsItem] = []
    seen_urls: set[str] = set()
    for card in parser.cards:
        title = re.sub(r"\s+", " ", card.title).strip()
        summary = re.sub(r"\s+", " ", card.excerpt).strip()
        if not title or not summary or not card.href:
            continue
        canonical_url, _ = urldefrag(urljoin(listing_url, card.href))
        if canonical_url in seen_urls:
            continue
        seen_urls.add(canonical_url)
        items.append(NtcNewsItem(canonical_url, title, summary, _parse_ntc_date(card.date)))
    return items[:MAX_ITEMS_PER_RUN]


class OfficialNtcNewsClient:
    """Bounded HTTP client for the public NTC listing page only."""

    async def fetch_listing(self) -> FetchedNtcListing:
        headers = {"User-Agent": "UNTverseNewsIngest/1.0 (+https://testcenter.kz/)"}
        timeout = httpx.Timeout(20.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = await client.get(NTC_NEWS_LISTING_URL)
            response.raise_for_status()
            if int(response.headers.get("content-length", 0) or 0) > MAX_RESPONSE_BYTES:
                raise ValueError("NTC listing response exceeds the configured size limit")
            raw = response.content
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("NTC listing response exceeds the configured size limit")
            final_url = str(response.url)
        if not final_url.startswith("https://testcenter.kz/"):
            raise ValueError("NTC listing redirected outside the official domain")
        raw_html = raw.decode(response.encoding or "utf-8", errors="replace")
        return FetchedNtcListing(final_url, raw_html, parse_ntc_listing(raw_html, final_url))


async def _store_listing_provenance(
    session: AsyncSession, source: Source, listing: FetchedNtcListing
) -> None:
    session.add(SourceDocument(
        source_id=source.id,
        url=listing.url,
        title="NTC public news listing",
        content_hash=hashlib.sha256(listing.raw_html.encode("utf-8")).hexdigest(),
        raw_content=listing.raw_html,
        content_type="text/html",
        http_status=200,
        doc_metadata={"kind": "ntc_news_listing", "items_discovered": len(listing.items)},
    ))


async def _try_acquire_postgres_lock(session: AsyncSession) -> bool:
    """Prevent concurrent production cron calls from duplicating a run."""
    bind = session.get_bind()
    if bind.dialect.name != "postgresql":
        return True
    # Transaction-scoped lock is released automatically on commit/rollback.
    result = await session.execute(text("SELECT pg_try_advisory_xact_lock(8142026)"))
    return bool(result.scalar())


async def run_daily_ntc_news_ingestion(
    *,
    client_factory: Callable[[], OfficialNtcNewsClient] = OfficialNtcNewsClient,
) -> dict[str, Any]:
    """Run one idempotent NTC ingestion batch against the configured application DB."""
    stats: dict[str, Any] = {
        "status": "success",
        "sources_processed": 0,
        "items_discovered": 0,
        "items_created": 0,
        "items_updated": 0,
        "items_skipped": 0,
        "items_failed": 0,
    }
    async with async_session_maker() as session:
        if not await _try_acquire_postgres_lock(session):
            return {**stats, "status": "already_running"}

        source = (await session.execute(
            select(Source).where(Source.slug == "testcenter-kz", Source.is_active.is_(True))
        )).scalar_one_or_none()
        if source is None:
            return {**stats, "status": "no_active_source"}

        stats["sources_processed"] = 1
        run = IngestionRun(source_id=source.id, job_name="daily_ntc_news_cron", status=IngestionRunStatus.RUNNING)
        session.add(run)
        await session.flush()
        source.last_checked_at = datetime.now(timezone.utc)

        try:
            listing = await client_factory().fetch_listing()
            if not listing.items:
                # The official home page normally retains recent cards. Treat an
                # empty parse as upstream markup drift, not a successful no-op.
                raise ValueError("No complete news cards found on the official NTC page")
            await _store_listing_provenance(session, source, listing)
            run.items_discovered = len(listing.items)
            stats["items_discovered"] = len(listing.items)
            engine = IngestionEngine(session)

            for item in listing.items:
                try:
                    result = await engine.ingest_news_item(
                        run_id=run.id,
                        source=source,
                        canonical_url=item.canonical_url,
                        title_kk=item.title_kk,
                        summary_kk=item.summary_kk,
                        content_kk=item.summary_kk,
                        published_at=item.published_at,
                    )
                    action = result["action"]
                    stats[f"items_{action}"] += 1
                    setattr(run, f"items_{action}", getattr(run, f"items_{action}") + 1)
                except Exception as exc:  # an invalid source item must not abort the batch
                    logger.warning("Could not ingest NTC item %s: %s", item.canonical_url, exc)
                    stats["items_failed"] += 1
                    run.items_failed += 1

            if run.items_failed == len(listing.items):
                run.status = IngestionRunStatus.FAILED
                run.error_summary = "Every parsed NTC news card failed ingestion"
            elif run.items_failed:
                run.status = IngestionRunStatus.PARTIAL
            else:
                run.status = IngestionRunStatus.SUCCESS
            stats["status"] = run.status
            if run.status != IngestionRunStatus.FAILED:
                source.last_success_at = datetime.now(timezone.utc)
        except Exception as exc:
            logger.exception("NTC news ingestion failed")
            run.status = IngestionRunStatus.FAILED
            run.items_failed += 1
            run.error_summary = str(exc)[:1000]
            stats["status"] = IngestionRunStatus.FAILED
            stats["items_failed"] += 1
        finally:
            run.completed_at = datetime.now(timezone.utc)
            await session.commit()
    return stats
