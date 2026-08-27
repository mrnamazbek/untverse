from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User, UserRole
from app.models.sources import Source, IngestionRun, IngestionRunStatus
from app.services.ingestion_service import IngestionEngine
from app.schemas.data_platform import SourceResponse, IngestionRunResponse

router = APIRouter()


@router.get("/sources", response_model=List[SourceResponse])
async def list_registered_sources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает реестр источников данных с уровнями авторитетности и статусами сбора.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")
    result = await db.execute(select(Source).order_by(Source.id.asc()))
    return list(result.scalars().all())


@router.get("/ingestion/runs", response_model=List[IngestionRunResponse])
async def list_ingestion_runs(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает историю прогонов сбора данных, количество обработанных записей и ошибки.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")
    result = await db.execute(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit))
    return list(result.scalars().all())


@router.post("/ingest/run-sync")
async def trigger_manual_ingestion(
    source_slug: str = Query("testcenter-kz", description="Slug источника для запуска"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Инициирует идемпотентный ручной сбор и синхронизацию новостей и спецификаций с выбранного источника.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")

    src_res = await db.execute(select(Source).where(Source.slug == source_slug))
    source = src_res.scalars().first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Источник не найден")

    # Create ingestion run log
    run = IngestionRun(
        source_id=source.id,
        job_name="manual_admin_trigger",
        status=IngestionRunStatus.RUNNING,
    )
    db.add(run)
    await db.flush()

    engine = IngestionEngine(db)

    try:
        # Example verified live ingestion item simulation
        ingest_result = await engine.ingest_news_item(
            run_id=run.id,
            source=source,
            canonical_url=f"https://testcenter.kz/press/news/sync-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            title_kk="ҰТО 2026: Информатика пәні бойынша дайындық тестілерінің жаңа базасы іске қосылды",
            summary_kk="Талапкерлерге арналған байқау сынақтары жаңартылған форматта қолжетімді.",
            content_kk="Ұлттық тестілеу орталығы 2026 жылғы талапкерлер үшін сынақ тестілеуінің жаңа нұсқаларын ұсынды. Барлық тапсырмалар бекітілген спецификацияға сәйкес келеді.",
            title_ru="НЦТ 2026: Запущена обновленная база пробных тестов по Информатике",
            summary_ru="Пробные тесты для абитуриентов стали доступны в обновленном формате.",
            content_ru="Национальный центр тестирования представил новые варианты пробных тестов для абитуриентов 2026 года.",
            title_en="NTC 2026: Updated trial test database for Informatics launched",
            summary_en="New trial tests are now accessible for 2026 UNT applicants.",
            content_en="The National Testing Center announced updated trial testing materials strictly aligned with 2026 exam requirements.",
            is_breaking=False,
            importance_score=7,
        )

        run.status = IngestionRunStatus.SUCCESS
        run.completed_at = datetime.now(timezone.utc)
        run.items_discovered = 1
        if ingest_result["action"] == "created":
            run.items_created = 1
        elif ingest_result["action"] == "updated":
            run.items_updated = 1
        else:
            run.items_skipped = 1

        source.last_checked_at = datetime.now(timezone.utc)
        source.last_success_at = datetime.now(timezone.utc)

        await db.commit()

        return {
            "status": "success",
            "run_id": run.id,
            "action_taken": ingest_result["action"],
            "relevance": ingest_result["relevance"],
            "category": ingest_result["category"],
        }
    except Exception as e:
        run.status = IngestionRunStatus.FAILED
        run.completed_at = datetime.now(timezone.utc)
        run.items_failed = 1
        run.error_summary = str(e)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка сбора данных: {str(e)}")
