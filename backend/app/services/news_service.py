from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from app.models.news import NewsArticle, NewsTranslation, NewsVersion, NewsSource, NewsStatus
from app.models.sources import Source


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_news(
        self,
        category: Optional[str] = None,
        locale: str = "kk",
        is_breaking: Optional[bool] = None,
        search_query: Optional[str] = None,
        limit: int = 15,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lists published news articles with translations, category filtering, and source provenance.
        """
        limit = min(max(1, limit), 50)

        stmt = select(NewsArticle).where(NewsArticle.status == NewsStatus.PUBLISHED)

        if category:
            stmt = stmt.where(NewsArticle.category == category)
        if is_breaking is not None:
            stmt = stmt.where(NewsArticle.is_breaking == is_breaking)

        if search_query and search_query.strip():
            term = f"%{search_query.strip()}%"
            stmt = stmt.join(NewsTranslation, NewsArticle.id == NewsTranslation.news_id).where(
                or_(
                    NewsTranslation.title.ilike(term),
                    NewsTranslation.summary.ilike(term)
                )
            )

        subq = stmt.with_only_columns(NewsArticle.id).order_by(None).subquery()
        count_stmt = select(func.count()).select_from(subq)
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = (
            stmt.options(
                selectinload(NewsArticle.translations),
                selectinload(NewsArticle.source),
            )
            .order_by(NewsArticle.is_breaking.desc(), NewsArticle.published_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        articles = result.scalars().unique().all()

        output = []
        for art in articles:
            trans = next((t for t in art.translations if t.locale == locale), None)
            if not trans and art.translations:
                trans = next((t for t in art.translations if t.locale == art.original_language), None)
            if not trans and art.translations:
                trans = art.translations[0]

            output.append({
                "id": art.id,
                "category": art.category,
                "importance_score": art.importance_score,
                "relevance_score": art.relevance_score,
                "is_breaking": art.is_breaking,
                "published_at": art.published_at.isoformat() if art.published_at else None,
                "last_verified_at": art.last_verified_at.isoformat() if art.last_verified_at else None,
                "canonical_url": art.canonical_url,
                "source_name": art.source.name if art.source else "ҰТО Ресми",
                "source_authority": art.source.authority_level if art.source else "official_primary",
                "title": trans.title if trans else "",
                "summary": trans.summary if trans else "",
                "locale": trans.locale if trans else locale,
            })

        return output, total

    async def get_news_article(self, news_id: int, locale: str = "kk") -> Optional[Dict[str, Any]]:
        """
        Retrieves full news article details with content, translations, and attribution.
        """
        stmt = (
            select(NewsArticle)
            .options(
                selectinload(NewsArticle.translations),
                selectinload(NewsArticle.source),
                selectinload(NewsArticle.versions),
            )
            .where(NewsArticle.id == news_id, NewsArticle.status == NewsStatus.PUBLISHED)
        )
        result = await self.session.execute(stmt)
        art = result.scalars().first()
        if not art:
            return None

        trans = next((t for t in art.translations if t.locale == locale), None)
        if not trans and art.translations:
            trans = art.translations[0]

        return {
            "id": art.id,
            "category": art.category,
            "importance_score": art.importance_score,
            "relevance_score": art.relevance_score,
            "is_breaking": art.is_breaking,
            "published_at": art.published_at.isoformat() if art.published_at else None,
            "last_verified_at": art.last_verified_at.isoformat() if art.last_verified_at else None,
            "canonical_url": art.canonical_url,
            "source_name": art.source.name if art.source else "ҰТО Ресми",
            "source_authority": art.source.authority_level if art.source else "official_primary",
            "title": trans.title if trans else "",
            "summary": trans.summary if trans else "",
            "content": trans.content if trans else "",
            "locale": trans.locale if trans else locale,
            "translation_source": trans.translation_source if trans else "official",
            "revision_count": len(art.versions),
        }

    async def get_breaking_alerts(self, locale: str = "kk") -> List[Dict[str, Any]]:
        """
        Returns urgent announcements and registration alerts for banner display.
        """
        stmt = (
            select(NewsArticle)
            .options(selectinload(NewsArticle.translations), selectinload(NewsArticle.source))
            .where(NewsArticle.is_breaking == True, NewsArticle.status == NewsStatus.PUBLISHED)
            .order_by(NewsArticle.published_at.desc())
            .limit(3)
        )
        result = await self.session.execute(stmt)
        articles = result.scalars().unique().all()

        output = []
        for art in articles:
            trans = next((t for t in art.translations if t.locale == locale), None)
            if not trans and art.translations:
                trans = art.translations[0]

            output.append({
                "id": art.id,
                "title": trans.title if trans else "",
                "summary": trans.summary if trans else "",
                "published_at": art.published_at.isoformat() if art.published_at else None,
                "canonical_url": art.canonical_url,
                "importance_score": art.importance_score,
            })

        return output
