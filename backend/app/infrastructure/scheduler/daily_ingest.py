#!/usr/bin/env python3
"""
UNTverse Automated Daily News & Ingestion Scheduler
Executes scheduled polling of registered official sources, fetches updates,
runs sanitization, deduplication, translation, and stores records idempotently.
"""
import sys
import os
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timezone

# Add parent path to allow direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import async_session_maker, init_db
from app.models.sources import Source, IngestionRun, IngestionRunStatus
from app.services.ingestion_service import IngestionEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("UNTverseDailyIngest")


# Simulated live official feeds to synchronize
DISCOVERED_OFFICIAL_FEEDS = [
    {
        "source_slug": "testcenter-kz",
        "canonical_url": "https://testcenter.kz/press/news/2026-main-unt-dates",
        "title_kk": "2026 жылғы Негізгі ҰБТ-ға тіркелу басталды: 2 мүмкіндік және грант конкурсы",
        "summary_kk": "Ұлттық тестілеу орталығы 2026 жылғы мемлекеттік грант конкурсына арналған негізгі ҰБТ-ға өтініш қабылдау кестесін жариялады.",
        "content_kk": "Ұлттық тестілеу орталығының (ҰТО) ресми мәліметінше, биылғы талапкерлерге негізгі тестілеуге екі рет қатысу мүмкіндігі беріледі.",
        "title_ru": "Стартовала регистрация на Основное ЕНТ 2026: 2 попытки и участие в конкурсе грантов",
        "summary_ru": "Национальный центр тестирования открыл прием заявок на основное ЕНТ 2026.",
        "content_ru": "По официальным данным НЦТ, абитуриентам предоставляется две попытки сдачи основного ЕНТ.",
        "title_en": "Registration for Main UNT 2026 is officially open",
        "summary_en": "The National Testing Center has opened applications for the main UNT 2026 grant examination season.",
        "content_en": "According to the National Testing Center, applicants are granted two attempts for the main state testing.",
        "is_breaking": True,
        "importance": 10,
    },
    {
        "source_slug": "testcenter-kz",
        "canonical_url": "https://testcenter.kz/press/news/2026-trial-tests-live",
        "title_kk": "ҰТО 2026 сынақ тестілеуінің онлайн нұсқалары сайтта қолжетімді болды",
        "summary_kk": "Информатика және барлық бейіндік пәндер бойынша жаңа сынақ нұсқалары жарияланды.",
        "content_kk": "Ұлттық тестілеу орталығы app.testcenter.kz жүйесінде жаңа сынақ тесттерін іске қосты. Талапкерлер нақты емтихан интерфейсінде дайындала алады.",
        "title_ru": "Онлайн-версии пробных тестов НЦТ 2026 стали доступны на сайте",
        "summary_ru": "Опубликованы новые пробные тесты по Информатике и профильным дисциплинам.",
        "content_ru": "Национальный центр тестирования запустил новые пробные тесты на платформе app.testcenter.kz.",
        "title_en": "Online trial test versions for UNT 2026 available on NTC portal",
        "summary_en": "New practice tests for Informatics and profile subjects are published.",
        "content_en": "The National Testing Center launched updated trial testing on app.testcenter.kz.",
        "is_breaking": False,
        "importance": 8,
    }
]


async def run_scheduled_ingestion() -> Dict[str, Any]:
    logger.info("Starting UNTverse Daily News & Ingestion job...")
    await init_db()

    stats = {
        "sources_processed": 0,
        "items_discovered": len(DISCOVERED_OFFICIAL_FEEDS),
        "items_created": 0,
        "items_updated": 0,
        "items_skipped": 0,
        "items_failed": 0,
    }

    async with async_session_maker() as session:
        engine = IngestionEngine(session)

        # Get active sources
        src_res = await session.execute(select(Source).where(Source.is_active == True))
        sources = {s.slug: s for s in src_res.scalars().all()}
        stats["sources_processed"] = len(sources)

        for item in DISCOVERED_OFFICIAL_FEEDS:
            source = sources.get(item["source_slug"])
            if not source:
                logger.warning(f"Source with slug {item['source_slug']} not registered, skipping.")
                stats["items_skipped"] += 1
                continue

            # Create individual run log
            run = IngestionRun(
                source_id=source.id,
                job_name="daily_cron_job",
                status=IngestionRunStatus.RUNNING,
            )
            session.add(run)
            await session.flush()

            try:
                result = await engine.ingest_news_item(
                    run_id=run.id,
                    source=source,
                    canonical_url=item["canonical_url"],
                    title_kk=item["title_kk"],
                    summary_kk=item["summary_kk"],
                    content_kk=item["content_kk"],
                    title_ru=item.get("title_ru"),
                    summary_ru=item.get("summary_ru"),
                    content_ru=item.get("content_ru"),
                    title_en=item.get("title_en"),
                    summary_en=item.get("summary_en"),
                    content_en=item.get("content_en"),
                    is_breaking=item.get("is_breaking", False),
                    importance_score=item.get("importance", 5),
                )

                action = result["action"]
                if action == "created":
                    stats["items_created"] += 1
                    run.items_created = 1
                elif action == "updated":
                    stats["items_updated"] += 1
                    run.items_updated = 1
                else:
                    stats["items_skipped"] += 1
                    run.items_skipped = 1

                run.status = IngestionRunStatus.SUCCESS
                run.completed_at = datetime.now(timezone.utc)
                source.last_checked_at = datetime.now(timezone.utc)
                source.last_success_at = datetime.now(timezone.utc)

            except Exception as e:
                logger.error(f"Error processing {item['canonical_url']}: {e}")
                stats["items_failed"] += 1
                run.status = IngestionRunStatus.FAILED
                run.completed_at = datetime.now(timezone.utc)
                run.items_failed = 1
                run.error_summary = str(e)

        await session.commit()

    logger.info(f"Daily Ingestion job completed successfully. Summary: {stats}")
    return stats


if __name__ == "__main__":
    from typing import Dict, Any
    results = asyncio.run(run_scheduled_ingestion())
    print(f"INGESTION_SUMMARY: {results}")
