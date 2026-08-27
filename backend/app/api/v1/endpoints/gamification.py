from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user, get_optional_current_user
from app.models.user import User
from app.services.gamification_service import GamificationService
from app.repositories.gamification_repo import GamificationRepository
from app.schemas.gamification import (
    GamificationProfileResponse, LeaderboardEntryResponse, AchievementResponse, DailyMissionResponse
)
from app.core.exceptions import BadRequestException

router = APIRouter()


@router.get("/profile", response_model=GamificationProfileResponse)
async def get_gamification_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = GamificationService(db)
    return await service.get_profile_gamification(current_user.id)


@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = GamificationRepository(db)
    user_id = current_user.id if current_user else 0
    raw = await repo.get_user_achievements(user_id)
    return [AchievementResponse(**ach) for ach in raw]


@router.get("/missions", response_model=List[DailyMissionResponse])
async def get_missions(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = GamificationRepository(db)
    user_id = current_user.id if current_user else 0
    raw = await repo.get_user_daily_missions(user_id)
    return [DailyMissionResponse(**m) for m in raw]


@router.get("/leaderboard", response_model=List[LeaderboardEntryResponse])
async def get_leaderboard(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    repo = GamificationRepository(db)
    raw = await repo.get_leaderboard(limit=limit)
    return [LeaderboardEntryResponse(**entry) for entry in raw]


@router.post("/missions/{mission_id}/claim")
async def claim_mission(
    mission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = GamificationRepository(db)
    reward_xp = await repo.claim_mission_reward(current_user.id, mission_id)
    if reward_xp is None:
        raise BadRequestException(detail="Задание еще не выполнено или награда уже получена")
    await db.commit()
    return {"message": "Награда получена", "xp_reward": reward_xp}
