"""Non-public endpoints invoked by the deployment scheduler."""
import hmac

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.services.ntc_news_ingestion import run_daily_ntc_news_ingestion

router = APIRouter()


@router.post("/daily-news-ingest", status_code=status.HTTP_200_OK, include_in_schema=False)
async def run_daily_news_ingest(x_unt_ingestion_key: str | None = Header(default=None)):
    """Run the NTC ingestion job; authentication is by deployment-only secret."""
    expected = settings.NEWS_INGESTION_SECRET
    if not expected or not x_unt_ingestion_key or not hmac.compare_digest(x_unt_ingestion_key, expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid ingestion credential")
    if settings.ENVIRONMENT == "production" and settings.DATABASE_URL.startswith("sqlite"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Production ingestion requires a PostgreSQL DATABASE_URL",
        )

    result = await run_daily_ntc_news_ingestion()
    if result["status"] == "already_running":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ingestion is already running")
    if result["status"] == "failed":
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Official NTC ingestion failed")
    return result
