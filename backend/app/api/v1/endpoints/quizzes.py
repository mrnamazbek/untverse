from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user, get_optional_current_user
from app.models.user import User
from app.services.quiz_service import QuizService
from app.schemas.quiz import (
    QuizListItem, QuizResponse, QuizSubmitRequest, QuizSubmitResponse
)

router = APIRouter()


@router.get("", response_model=List[QuizListItem])
async def list_quizzes(
    quiz_type: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = QuizService(db)
    user_id = current_user.id if current_user else None
    return await service.list_quizzes(user_id=user_id, quiz_type=quiz_type)


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = QuizService(db)
    return await service.get_quiz_for_student(quiz_id=quiz_id)


@router.post("/{quiz_id}/attempts", response_model=QuizSubmitResponse)
async def submit_quiz_attempt(
    quiz_id: int,
    request: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = QuizService(db)
    response = await service.submit_quiz(user_id=current_user.id, quiz_id=quiz_id, request=request)
    await db.commit()
    return response
