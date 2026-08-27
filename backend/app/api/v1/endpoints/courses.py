from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user, get_optional_current_user
from app.models.user import User
from app.services.learning_service import LearningService
from app.schemas.course import CourseResponse, TopicResponse, LessonResponse, LessonCompleteResponse

router = APIRouter()


@router.get("", response_model=List[CourseResponse])
async def get_courses(
    locale: str = Query("kk", pattern="^(kk|ru|en)$"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LearningService(db)
    user_id = current_user.id if current_user else None
    return await service.get_courses_hierarchy(user_id=user_id, locale=locale)


@router.get("/topics/{slug}", response_model=TopicResponse)
async def get_topic(
    slug: str,
    locale: str = Query("kk", pattern="^(kk|ru|en)$"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LearningService(db)
    user_id = current_user.id if current_user else None
    return await service.get_topic_detail(slug=slug, user_id=user_id, locale=locale)


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    locale: str = Query("kk", pattern="^(kk|ru|en)$"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LearningService(db)
    user_id = current_user.id if current_user else None
    return await service.get_lesson_detail(lesson_id=lesson_id, user_id=user_id, locale=locale)


@router.post("/lessons/{lesson_id}/complete", response_model=LessonCompleteResponse)
async def complete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LearningService(db)
    resp = await service.complete_lesson(user_id=current_user.id, lesson_id=lesson_id)
    await db.commit()
    return resp
