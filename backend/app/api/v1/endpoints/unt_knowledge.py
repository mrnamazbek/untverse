from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.specification_service import SpecificationService
from app.schemas.data_platform import CurrentUntRuleResponse, ExamSpecificationResponse

router = APIRouter()


@router.get("/current", response_model=CurrentUntRuleResponse)
async def get_current_unt_rules(
    year: Optional[int] = Query(None, description="Год экзамена (по умолчанию актуальный)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает актуальные верифицированные правила ЕНТ/ҰБТ текущего сезона:
    шкала баллов, длительность, пороговые значения, периоды сдачи, комбинации профилей и дедлайны.
    """
    service = SpecificationService(db)
    rules = await service.get_current_unt_rules(exam_year=year)
    if not rules:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Правила для указанного года не найдены")
    return rules


@router.get("/specifications", response_model=List[ExamSpecificationResponse])
async def get_exam_specifications(
    locale: str = Query("kk", description="Язык спецификации (kk, ru, en)"),
    year: Optional[int] = Query(None, description="Год спецификации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает официальные спецификации экзамена по Информатике с полной иерархической таксономией тем.
    """
    service = SpecificationService(db)
    return await service.get_informatics_specifications(locale=locale, year=year)
