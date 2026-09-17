"""Non-public endpoints invoked by the deployment scheduler."""

import hmac

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.services.ntc_news_ingestion import run_daily_ntc_news_ingestion

router = APIRouter()


def _has_valid_manual_credential(provided: str | None) -> bool:
    expected = settings.NEWS_INGESTION_SECRET
    return bool(expected and provided and hmac.compare_digest(provided, expected))


def _has_valid_vercel_cron_credential(authorization: str | None) -> bool:
    expected = settings.CRON_SECRET
    provided = authorization.removeprefix("Bearer ") if authorization else None
    return bool(expected and provided and hmac.compare_digest(provided, expected))


async def _run_daily_news_ingest() -> dict:
    if settings.ENVIRONMENT == "production" and settings.DATABASE_URL.startswith("sqlite"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Production ingestion requires a PostgreSQL DATABASE_URL",
        )

    result = await run_daily_ntc_news_ingestion()
    if result["status"] == "already_running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ingestion is already running"
        )
    if result["status"] == "failed":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Official NTC ingestion failed"
        )
    return result


@router.post("/daily-news-ingest", status_code=status.HTTP_200_OK, include_in_schema=False)
async def run_daily_news_ingest(x_unt_ingestion_key: str | None = Header(default=None)):
    """Run the NTC ingestion job; authentication is by deployment-only secret."""
    if not _has_valid_manual_credential(x_unt_ingestion_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid ingestion credential"
        )
    return await _run_daily_news_ingest()


@router.get("/daily-news-ingest", status_code=status.HTTP_200_OK, include_in_schema=False)
async def run_vercel_daily_news_ingest(authorization: str | None = Header(default=None)):
    """Vercel Cron adapter; Vercel calls scheduled paths with an HTTP GET."""
    if not _has_valid_vercel_cron_credential(authorization):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid cron credential")
    return await _run_daily_news_ingest()
