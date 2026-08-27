from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User, UserRole
from app.models.sources import Source, IngestionRun
from app.services.ntc_news_ingestion import run_daily_ntc_news_ingestion
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
    Инициирует ручной идемпотентный сбор опубликованных новостей с официального сайта НЦТ.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")

    if source_slug != "testcenter-kz":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ручной сбор пока поддерживается только для официального источника testcenter-kz",
        )

    result = await run_daily_ntc_news_ingestion()
    if result["status"] == "already_running":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Сбор уже выполняется")
    if result["status"] == "failed":
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Не удалось получить новости с НЦТ")
    return result
