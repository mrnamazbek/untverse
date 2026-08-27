from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.glossary_service import KazakhLanguageQAService
from app.schemas.data_platform import GlossaryTermResponse, KazakhQARequest, KazakhQAResponse

router = APIRouter()


@router.get("/glossary", response_model=List[GlossaryTermResponse])
async def get_glossary_terms(
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает утвержденный глоссарий официальной терминологии Казахстана на 3 языках (kk, ru, en).
    """
    qa_service = KazakhLanguageQAService(db)
    return await qa_service.get_all_glossary_terms()


@router.post("/kazakh-qa", response_model=KazakhQAResponse)
async def check_kazakh_text_quality(
    payload: KazakhQARequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверяет текст на казахском языке на механические кальки, орфографические соответствия и естественность.
    """
    qa_service = KazakhLanguageQAService(db)
    result = qa_service.validate_kazakh_text(payload.text)
    return result
