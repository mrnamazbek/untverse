from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class XpTransactionResponse(BaseModel):
    id: int
    amount: int
    reason: str
    reference_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AchievementResponse(BaseModel):
    id: int
    code: str
    title: str
    description: str
    icon: str
    badge_color: str
    category: str
    xp_reward: int
    condition_type: str
    condition_value: int
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DailyMissionResponse(BaseModel):
    id: int
    title: str
    description: str
    mission_type: str
    target_count: int
    xp_reward: int
    icon: str
    current_progress: int = 0
    is_completed: bool = False
    is_claimed: bool = False

    model_config = ConfigDict(from_attributes=True)


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
    freeze_count: int
    is_active_today: bool

    model_config = ConfigDict(from_attributes=True)


class LeaderboardEntryResponse(BaseModel):
    rank: int
    user_id: int
    display_name: str
    avatar_url: Optional[str] = None
    level: int
    rank_title: str
    total_xp: int
    streak_count: int

    model_config = ConfigDict(from_attributes=True)


class GamificationProfileResponse(BaseModel):
    user_id: int
    display_name: str
    avatar_url: Optional[str] = None
    current_level: int
    current_xp: int
    next_level_xp: int
    level_progress_percentage: float
    rank_title: str
    streak: StreakResponse
    recent_achievements: List[AchievementResponse] = []
    daily_missions: List[DailyMissionResponse] = []

    model_config = ConfigDict(from_attributes=True)
