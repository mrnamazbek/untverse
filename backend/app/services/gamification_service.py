from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.gamification_repo import GamificationRepository
from app.repositories.user_repo import UserRepository
from app.core.events import (
    dispatcher, DomainEvent, QuizCompletedEvent, LessonCompletedEvent,
    CodingTaskCompletedEvent, DailyLoginEvent
)
from app.schemas.gamification import GamificationProfileResponse, StreakResponse, AchievementResponse, DailyMissionResponse


class GamificationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.gamification_repo = GamificationRepository(session)
        self.user_repo = UserRepository(session)

    async def get_profile_gamification(self, user_id: int) -> GamificationProfileResponse:
        user = await self.user_repo.get_with_profile(user_id)
        if not user or not user.profile:
            raise ValueError(f"User {user_id} not found")

        p = user.profile
        streak = await self.gamification_repo.get_or_create_streak(user_id)
        achievements_raw = await self.gamification_repo.get_user_achievements(user_id)
        missions_raw = await self.gamification_repo.get_or_create_daily_missions(user_id)

        # Calculate XP requirements for current and next level
        # Level N requires: total_xp >= 150 * (N - 1)^2
        current_lvl_base_xp = 150 * ((p.current_level - 1) ** 2)
        next_lvl_base_xp = 150 * (p.current_level ** 2)
        xp_in_level = max(0, p.total_xp - current_lvl_base_xp)
        xp_needed_for_level = max(1, next_lvl_base_xp - current_lvl_base_xp)
        level_pct = min(100.0, round((xp_in_level / xp_needed_for_level) * 100, 1))

        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date()
        is_active_today = streak.last_activity_date == today

        return GamificationProfileResponse(
            user_id=p.user_id,
            display_name=p.display_name,
            avatar_url=p.avatar_url,
            current_level=p.current_level,
            current_xp=p.total_xp,
            next_level_xp=next_lvl_base_xp,
            level_progress_percentage=level_pct,
            rank_title=p.rank_title,
            streak=StreakResponse(
                current_streak=streak.current_streak,
                longest_streak=streak.longest_streak,
                last_activity_date=streak.last_activity_date,
                freeze_count=streak.freeze_count,
                is_active_today=is_active_today
            ),
            recent_achievements=[AchievementResponse(**a) for a in achievements_raw],
            daily_missions=[DailyMissionResponse(**m) for m in missions_raw]
        )

    async def check_and_unlock_achievements(self, user_id: int):
        """
        Evaluates user stats and unlocks achievements if criteria are met.
        """
        user = await self.user_repo.get_with_profile(user_id)
        if not user or not user.profile:
            return

        p = user.profile
        streak = await self.gamification_repo.get_or_create_streak(user_id)

        # 1. Level achievements
        if p.current_level >= 5:
            await self.gamification_repo.unlock_achievement(user_id, "level_5")
        if p.current_level >= 10:
            await self.gamification_repo.unlock_achievement(user_id, "level_10")
        if p.current_level >= 20:
            await self.gamification_repo.unlock_achievement(user_id, "level_20")

        # 2. Streak achievements
        if streak.current_streak >= 3:
            await self.gamification_repo.unlock_achievement(user_id, "streak_3")
        if streak.current_streak >= 7:
            await self.gamification_repo.unlock_achievement(user_id, "streak_7")
        if streak.current_streak >= 30:
            await self.gamification_repo.unlock_achievement(user_id, "streak_30")

    async def handle_quiz_completed(self, event: QuizCompletedEvent) -> Dict[str, Any]:
        # 1. Award XP based on percentage and speed
        base_xp = 30
        bonus_xp = int(event.percentage * 0.5)  # up to 50 XP
        if event.percentage == 100.0:
            bonus_xp += 20  # Perfect score bonus
        total_awarded = base_xp + bonus_xp

        new_total_xp, new_level, leveled_up = await self.gamification_repo.add_xp(
            user_id=event.user_id,
            amount=total_awarded,
            reason="quiz_completed",
            reference_id=f"quiz_{event.quiz_id}"
        )

        # 2. Update streak
        current_streak, is_extended = await self.gamification_repo.update_activity_streak(event.user_id)

        # 3. Update missions
        await self.gamification_repo.update_mission_progress(event.user_id, "complete_quiz", 1)
        await self.gamification_repo.update_mission_progress(event.user_id, "answer_questions", event.total_count)

        # 4. Check achievements
        if event.percentage == 100.0:
            await self.gamification_repo.unlock_achievement(event.user_id, "perfect_quiz_first")
        await self.gamification_repo.unlock_achievement(event.user_id, "first_quiz")
        await self.check_and_unlock_achievements(event.user_id)

        return {
            "xp_earned": total_awarded,
            "new_total_xp": new_total_xp,
            "new_level": new_level,
            "leveled_up": leveled_up,
            "streak_extended": is_extended,
            "current_streak": current_streak
        }

    async def handle_lesson_completed(self, user_id: int, lesson_id: int, xp_reward: int = 25) -> Tuple[int, int, bool]:
        new_total_xp, new_level, leveled_up = await self.gamification_repo.add_xp(
            user_id=user_id,
            amount=xp_reward,
            reason="lesson_completed",
            reference_id=f"lesson_{lesson_id}"
        )
        await self.gamification_repo.update_activity_streak(user_id)
        await self.gamification_repo.update_mission_progress(user_id, "read_lesson", 1)
        await self.gamification_repo.unlock_achievement(user_id, "first_lesson")
        await self.check_and_unlock_achievements(user_id)
        return (new_total_xp, new_level, leveled_up)

    async def handle_coding_task_completed(self, user_id: int, task_id: int, xp_reward: int = 75) -> Tuple[int, int, bool]:
        new_total_xp, new_level, leveled_up = await self.gamification_repo.add_xp(
            user_id=user_id,
            amount=xp_reward,
            reason="coding_task_completed",
            reference_id=f"task_{task_id}"
        )
        await self.gamification_repo.update_activity_streak(user_id)
        await self.gamification_repo.update_mission_progress(user_id, "solve_coding", 1)
        await self.gamification_repo.unlock_achievement(user_id, "first_code_task")
        await self.check_and_unlock_achievements(user_id)
        return (new_total_xp, new_level, leveled_up)
