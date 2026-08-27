from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.db.session import get_db
from app.models.course import Topic, Lesson
from app.models.news import NewsArticle, NewsTranslation, NewsStatus
from app.models.question_bank import BankQuestion, QuestionTranslation

router = APIRouter()


@router.get("")
async def unified_search(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    locale: str = Query("kk", description="Язык контента (kk, ru, en)"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Единый мультиязычный поиск по всей платформе UNTverse: вопросы, темы, уроки и новости ЕНТ.
    """
    term = f"%{q.strip()}%"

    # 1. Search Questions
    q_stmt = (
        select(BankQuestion, QuestionTranslation)
        .join(QuestionTranslation, BankQuestion.id == QuestionTranslation.question_id)
        .where(
            BankQuestion.is_active == True,
            QuestionTranslation.locale == locale,
            or_(
                QuestionTranslation.text.ilike(term),
                QuestionTranslation.explanation.ilike(term),
            )
        )
        .limit(limit // 3 + 2)
    )
    q_res = await db.execute(q_stmt)
    questions_results = [
        {
            "type": "question",
            "id": row[0].id,
            "title": row[1].text[:120] + "..." if len(row[1].text) > 120 else row[1].text,
            "snippet": row[1].explanation[:150] if row[1].explanation else "",
            "difficulty": row[0].difficulty,
            "url": f"/practice?question_id={row[0].id}",
        }
        for row in q_res.all()
    ]

    # 2. Search Topics & Lessons
    t_stmt = (
        select(Topic)
        .where(or_(Topic.title.ilike(term), Topic.description.ilike(term)))
        .limit(limit // 3 + 2)
    )
    t_res = await db.execute(t_stmt)
    topics_results = [
        {
            "type": "topic",
            "id": top.id,
            "title": top.title,
            "snippet": top.description[:150],
            "url": f"/learn/{top.slug}",
        }
        for top in t_res.scalars().all()
    ]

    # 3. Search News
    n_stmt = (
        select(NewsArticle, NewsTranslation)
        .join(NewsTranslation, NewsArticle.id == NewsTranslation.news_id)
        .where(
            NewsArticle.status == NewsStatus.PUBLISHED,
            NewsTranslation.locale == locale,
            or_(
                NewsTranslation.title.ilike(term),
                NewsTranslation.summary.ilike(term),
                NewsTranslation.content.ilike(term),
            )
        )
        .limit(limit // 3 + 2)
    )
    n_res = await db.execute(n_stmt)
    news_results = [
        {
            "type": "news",
            "id": row[0].id,
            "title": row[1].title,
            "snippet": row[1].summary[:150],
            "category": row[0].category,
            "url": f"/news/{row[0].id}",
        }
        for row in n_res.all()
    ]

    combined = questions_results + topics_results + news_results
    return {
        "query": q,
        "locale": locale,
        "total_matches": len(combined),
        "results": combined[:limit],
    }
