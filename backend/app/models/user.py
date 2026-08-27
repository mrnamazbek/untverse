from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.STUDENT.value, nullable=False, index=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    coding_submissions: Mapped[List["CodingSubmission"]] = relationship("CodingSubmission", back_populates="user", cascade="all, delete-orphan")
    xp_transactions: Mapped[List["XpTransaction"]] = relationship("XpTransaction", back_populates="user", cascade="all, delete-orphan")
    user_achievements: Mapped[List["UserAchievement"]] = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    user_missions: Mapped[List["UserMission"]] = relationship("UserMission", back_populates="user", cascade="all, delete-orphan")
    streak: Mapped[Optional["Streak"]] = relationship("Streak", back_populates="user", uselist=False, cascade="all, delete-orphan")
    topic_masteries: Mapped[List["TopicMastery"]] = relationship("TopicMastery", back_populates="user", cascade="all, delete-orphan")
    spaced_cards: Mapped[List["SpacedRepetitionCard"]] = relationship("SpacedRepetitionCard", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_unt_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    current_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    rank_title: Mapped[str] = mapped_column(String(100), default="Новичок Информатики", nullable=False)
    streak_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="profile")

    __table_args__ = (
        Index("idx_user_profiles_xp_rank", "total_xp", "current_level"),
    )


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
