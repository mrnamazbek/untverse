from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.question_bank_service import QuestionBankService
from app.services.question_selection_service import QuestionSelectionService
from app.schemas.data_platform import (
    BankQuestionResponse, BankQuestionDetailResponse, QuestionListResponse
)

router = APIRouter()


@router.get("", response_model=QuestionListResponse)
async def list_questions(
    subject: str = Query("informatics", description="Код предмета"),
    section_id: Optional[int] = Query(None, description="ID раздела спецификации"),
    topic_id: Optional[int] = Query(None, description="ID темы спецификации"),
    difficulty: Optional[str] = Query(None, description="Сложность (A, B, C)"),
    year: Optional[int] = Query(None, description="Год вопроса"),
    question_type: Optional[str] = Query(None, description="Тип вопроса"),
    official_status: Optional[str] = Query(None, description="Статус (official, official_sample, etc.)"),
    locale: str = Query("kk", description="Язык (kk, ru, en)"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Полнофункциональный поиск и фильтрация банка вопросов ЕНТ по предмету, разделу, теме, сложности и языку.
    """
    service = QuestionBankService(db)
    items, total = await service.list_questions(
        subject_code=subject,
        section_id=section_id,
        topic_id=topic_id,
        difficulty=difficulty,
        year=year,
        question_type=question_type,
        official_status=official_status,
        locale=locale,
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


@router.get("/practice/sample", response_model=List[BankQuestionResponse])
async def sample_practice_questions(
    topic_id: int = Query(..., description="ID темы спецификации"),
    count: int = Query(10, ge=1, le=30),
    difficulty: Optional[str] = Query(None, description="Сложность (A, B, C)"),
    locale: str = Query("kk", description="Язык контента"),
    db: AsyncSession = Depends(get_db)
):
    """
    Высокопроизводительная выборка вопросов для тренировки по теме без дорогих ORDER BY random().
    """
    selection_service = QuestionSelectionService(db)
    return await selection_service.sample_by_topic(
        specification_topic_id=topic_id,
        count=count,
        difficulty=difficulty,
        locale=locale,
    )


@router.get("/practice/unt-mock", response_model=List[BankQuestionResponse])
async def generate_unt_50_mock_exam(
    locale: str = Query("kk", description="Язык экзамена (kk, ru, en)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Генератор полного сбалансированного пробного ЕНТ из 50 вопросов по официальной структуре НЦТ РК.
    """
    selection_service = QuestionSelectionService(db)
    return await selection_service.generate_unt_50_mock(locale=locale)


@router.get("/{id}", response_model=BankQuestionDetailResponse)
async def get_question_detail(
    id: int,
    locale: str = Query("kk", description="Язык контента (kk, ru, en)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает детальную карточку вопроса с вариантами ответов, пошаговым разбором и провенансом.
    """
    service = QuestionBankService(db)
    question = await service.get_question_by_id(question_id=id, locale=locale)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")
    return question
