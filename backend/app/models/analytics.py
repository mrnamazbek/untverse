from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Boolean, Integer, ForeignKey, Float, Index, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class TopicMastery(Base, TimestampMixin):
    __tablename__ = "topic_masteries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False)
    mastery_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="topic_masteries")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="masteries")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_mastery"),
        Index("idx_topic_masteries_user_pct", "user_id", "mastery_percentage"),
    )


class MistakeLog(Base, TimestampMixin):
    __tablename__ = "mistake_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_mistake_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    question: Mapped["Question"] = relationship("Question", back_populates="mistakes")

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question_mistake"),
        Index("idx_mistake_logs_unresolved", "user_id", "is_resolved"),
    )


class SpacedRepetitionCard(Base, TimestampMixin):
    """
    SuperMemo SM-2 Interval algorithm model for optimal question recall
    """
    __tablename__ = "spaced_repetition_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    repetition_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="spaced_cards")
    question: Mapped["Question"] = relationship("Question")

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_srs_card"),
        Index("idx_srs_due_review", "user_id", "next_review_at"),
    )
