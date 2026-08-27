from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.gamification_service import GamificationService
from app.repositories.gamification_repo import GamificationRepository
from app.schemas.gamification import (
    GamificationProfileResponse, LeaderboardEntryResponse
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
