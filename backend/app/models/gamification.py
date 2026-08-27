from typing import Optional, List
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Date, Index, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class XpTransaction(Base, TimestampMixin):
    __tablename__ = "xp_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)  # quiz_passed, lesson_read, coding_task, streak_bonus, daily_quest, achievement
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="xp_transactions")

    __table_args__ = (
        Index("idx_xp_transactions_user_date", "user_id", "created_at"),
    )


class Achievement(Base, TimestampMixin):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(100), default="award", nullable=False)
    badge_color: Mapped[str] = mapped_column(String(50), default="purple", nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)  # streaks, quizzes, coding, mastery, speed
    xp_reward: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False)  # streak_days, total_quizzes, perfect_quizzes, python_tasks, level_reached
    condition_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user_achievements: Mapped[List["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base, TimestampMixin):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), index=True, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )


class DailyMission(Base, TimestampMixin):
    __tablename__ = "daily_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mission_type: Mapped[str] = mapped_column(String(50), nullable=False)  # answer_questions, complete_quiz, solve_coding, review_mistakes, read_lesson
    target_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="target", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserMission(Base, TimestampMixin):
    __tablename__ = "user_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    mission_id: Mapped[int] = mapped_column(Integer, ForeignKey("daily_missions.id", ondelete="CASCADE"), index=True, nullable=False)
    mission_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    current_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    target_progress: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="user_missions")
    mission: Mapped["DailyMission"] = relationship("DailyMission")

    __table_args__ = (
        UniqueConstraint("user_id", "mission_id", "mission_date", name="uq_user_mission_date"),
    )


class Streak(Base, TimestampMixin):
    __tablename__ = "streaks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    freeze_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="streak")
