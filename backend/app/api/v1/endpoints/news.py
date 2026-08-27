from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.news_service import NewsService
from app.schemas.data_platform import (
    NewsArticleResponse, NewsArticleDetailResponse, NewsListResponse, NewsAlertResponse
)

router = APIRouter()


@router.get("", response_model=NewsListResponse)
async def list_news_articles(
    category: Optional[str] = Query(None, description="Категория (unt, registration, grants, informatics)"),
    locale: str = Query("kk", description="Язык контента (kk, ru, en)"),
    is_breaking: Optional[bool] = Query(None, description="Только срочные новости"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    limit: int = Query(15, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает список актуальных верифицированных новостей ЕНТ с локализацией и атрибуцией источников.
    """
    service = NewsService(db)
    items, total = await service.list_news(
        category=category,
        locale=locale,
        is_breaking=is_breaking,
        search_query=search,
        limit=limit,
        offset=offset,
    )
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/alerts", response_model=List[NewsAlertResponse])
async def get_breaking_alerts(
    locale: str = Query("kk", description="Язык (kk, ru, en)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает срочные оповещения и напоминания о дедлайнах для баннеров интерфейса.
    """
    service = NewsService(db)
    return await service.get_breaking_alerts(locale=locale)


@router.get("/{id}", response_model=NewsArticleDetailResponse)
async def get_news_article_detail(
    id: int,
    locale: str = Query("kk", description="Язык (kk, ru, en)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает полную статью с текстом, переводом, историей правок и ссылкой на первоисточник.
    """
    service = NewsService(db)
    article = await service.get_news_article(news_id=id, locale=locale)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Новость не найдена")
    return article
