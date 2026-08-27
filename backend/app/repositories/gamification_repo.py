from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import selectinload
from app.models.gamification import (
    XpTransaction, Achievement, UserAchievement, DailyMission, UserMission, Streak
)
from app.models.user import UserProfile, User
from app.repositories.base import BaseRepository


class GamificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_xp(self, user_id: int, amount: int, reason: str, reference_id: Optional[str] = None) -> Tuple[int, int, bool]:
        """
        Records XP transaction and updates UserProfile.
        Returns: (new_total_xp, new_level, leveled_up)
        """
        tx = XpTransaction(
            user_id=user_id,
            amount=amount,
            reason=reason,
            reference_id=reference_id
        )
        self.session.add(tx)
        await self.session.flush()

        # Update profile
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalars().first()
        if not profile:
            return (amount, 1, False)

        old_level = profile.current_level
        profile.total_xp += amount
        
        # Level formula: level = 1 + int((total_xp / 150) ** 0.5)
        # Level 1: 0-149 XP, Level 2: 150-599 XP, Level 3: 600-1349 XP, etc.
        new_level = max(1, 1 + int((profile.total_xp / 150) ** 0.5))
        leveled_up = new_level > old_level
        profile.current_level = new_level

        # Calculate Rank Title
        if new_level >= 20:
            profile.rank_title = "Магистр Информатики ЕНТ"
        elif new_level >= 15:
            profile.rank_title = "Сеньор Алгоритмов"
        elif new_level >= 10:
            profile.rank_title = "Продвинутый Программист"
        elif new_level >= 5:
            profile.rank_title = "Студент-Исследователь"
        else:
            profile.rank_title = "Новичок Информатики"

        await self.session.flush()
        return (profile.total_xp, profile.current_level, leveled_up)

    async def get_or_create_streak(self, user_id: int) -> Streak:
        result = await self.session.execute(
            select(Streak).where(Streak.user_id == user_id)
        )
        streak = result.scalars().first()
        if not streak:
            streak = Streak(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                last_activity_date=None,
                freeze_count=0
            )
            self.session.add(streak)
            await self.session.flush()
        return streak

    async def update_activity_streak(self, user_id: int) -> Tuple[int, bool]:
        """
        Updates streak for user. Returns (current_streak, is_extended)
        """
        streak = await self.get_or_create_streak(user_id)
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        is_extended = False

        if streak.last_activity_date == today:
            # Already recorded today
            return (streak.current_streak, False)
        elif streak.last_activity_date == yesterday:
            # Maintained streak!
            streak.current_streak += 1
            is_extended = True
        else:
            # Broken streak or first day
            streak.current_streak = 1
            is_extended = True

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        streak.last_activity_date = today

        # Update UserProfile streak_count as well
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalars().first()
        if profile:
            profile.streak_count = streak.current_streak

        await self.session.flush()
        return (streak.current_streak, is_extended)

    async def get_user_achievements(self, user_id: int) -> List[dict]:
        all_achievements_res = await self.session.execute(select(Achievement).order_by(Achievement.id))
        all_achievements = all_achievements_res.scalars().all()

        user_achievements_res = await self.session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        unlocked_map = {ua.achievement_id: ua.unlocked_at for ua in user_achievements_res.scalars().all()}

        output = []
        for ach in all_achievements:
            is_unlocked = ach.id in unlocked_map
            output.append({
                "id": ach.id,
                "code": ach.code,
                "title": ach.title,
                "description": ach.description,
                "icon": ach.icon,
                "badge_color": ach.badge_color,
                "category": ach.category,
                "xp_reward": ach.xp_reward,
                "condition_type": ach.condition_type,
                "condition_value": ach.condition_value,
                "is_unlocked": is_unlocked,
                "unlocked_at": unlocked_map.get(ach.id)
            })
        return output

    async def unlock_achievement(self, user_id: int, achievement_code: str) -> Optional[Achievement]:
        ach_res = await self.session.execute(
            select(Achievement).where(Achievement.code == achievement_code)
        )
        ach = ach_res.scalars().first()
        if not ach:
            return None

        # Check if already unlocked
        existing = await self.session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == ach.id
            )
        )
        if existing.scalars().first():
            return None

        ua = UserAchievement(
            user_id=user_id,
            achievement_id=ach.id,
            unlocked_at=datetime.now(timezone.utc)
        )
        self.session.add(ua)
        await self.session.flush()

        # Award XP for achievement
        await self.add_xp(user_id, ach.xp_reward, reason="achievement_unlocked", reference_id=ach.code)
        return ach

    async def get_or_create_daily_missions(self, user_id: int) -> List[dict]:
        today = datetime.now(timezone.utc).date()
        active_missions_res = await self.session.execute(
            select(DailyMission).where(DailyMission.is_active == True)
        )
        active_missions = active_missions_res.scalars().all()

        output = []
        for m in active_missions:
            um_res = await self.session.execute(
                select(UserMission).where(
                    UserMission.user_id == user_id,
                    UserMission.mission_id == m.id,
                    UserMission.mission_date == today
                )
            )
            um = um_res.scalars().first()
            if not um:
                um = UserMission(
                    user_id=user_id,
                    mission_id=m.id,
                    mission_date=today,
                    current_progress=0,
                    target_progress=m.target_count,
                    is_completed=False,
                    claimed_at=None
                )
                self.session.add(um)
                await self.session.flush()

            output.append({
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "mission_type": m.mission_type,
                "target_count": m.target_count,
                "xp_reward": m.xp_reward,
                "icon": m.icon,
                "current_progress": um.current_progress,
                "is_completed": um.is_completed,
                "is_claimed": um.claimed_at is not None
            })
        return output

    async def update_mission_progress(self, user_id: int, mission_type: str, increment: int = 1):
        today = datetime.now(timezone.utc).date()
        missions = await self.get_or_create_daily_missions(user_id)
        for m in missions:
            if m["mission_type"] == mission_type and not m["is_completed"]:
                res = await self.session.execute(
                    select(UserMission).where(
                        UserMission.user_id == user_id,
                        UserMission.mission_id == m["id"],
                        UserMission.mission_date == today
                    )
                )
                um = res.scalars().first()
                if um:
                    um.current_progress += increment
                    if um.current_progress >= um.target_progress:
                        um.current_progress = um.target_progress
                        um.is_completed = True
                    await self.session.flush()

    async def claim_mission_reward(self, user_id: int, mission_id: int) -> Optional[int]:
        today = datetime.now(timezone.utc).date()
        res = await self.session.execute(
            select(UserMission, DailyMission)
            .join(DailyMission, DailyMission.id == UserMission.mission_id)
            .where(
                UserMission.user_id == user_id,
                UserMission.mission_id == mission_id,
                UserMission.mission_date == today
            )
        )
        row = res.first()
        if not row:
            return None
        um, m = row
        if not um.is_completed or um.claimed_at is not None:
            return None

        um.claimed_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.add_xp(user_id, m.xp_reward, reason="daily_mission_claimed", reference_id=f"mission_{m.id}")
        return m.xp_reward

    async def get_leaderboard(self, limit: int = 50) -> List[dict]:
        result = await self.session.execute(
            select(UserProfile)
            .order_by(UserProfile.total_xp.desc(), UserProfile.current_level.desc())
            .limit(limit)
        )
        profiles = result.scalars().all()
        leaderboard = []
        for rank, p in enumerate(profiles, start=1):
            leaderboard.append({
                "rank": rank,
                "user_id": p.user_id,
                "display_name": p.display_name,
                "avatar_url": p.avatar_url,
                "level": p.current_level,
                "rank_title": p.rank_title,
                "total_xp": p.total_xp,
                "streak_count": p.streak_count
            })
        return leaderboard
