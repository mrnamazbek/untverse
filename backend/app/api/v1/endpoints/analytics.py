from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_teacher_or_admin
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    StudentAnalyticsDashboard, MistakeItem, SpacedCardReviewItem, SpacedReviewSubmit
)

router = APIRouter()


@router.get("/dashboard", response_model=StudentAnalyticsDashboard)
async def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_student_dashboard(current_user.id)


@router.get("/mistakes", response_model=List[MistakeItem])
async def get_mistakes_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_unresolved_mistakes(current_user.id)


@router.get("/srs/due", response_model=List[SpacedCardReviewItem])
async def get_due_spaced_cards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_due_spaced_repetition_cards(current_user.id)


@router.post("/srs/review")
async def submit_spaced_card_review(
    submit: SpacedReviewSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    res = await service.submit_spaced_review(current_user.id, submit)
    await db.commit()
    return res


@router.get("/teacher", dependencies=[Depends(require_teacher_or_admin)])
async def get_teacher_analytics(
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_teacher_class_analytics()
