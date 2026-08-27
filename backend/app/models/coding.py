from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Float, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class CodingTask(Base, TimestampMixin):
    __tablename__ = "coding_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown description with constraints & I/O format
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    solution_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # easy, medium, hard
    time_limit_seconds: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=75, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="coding_tasks")
    test_cases: Mapped[List["TestCase"]] = relationship("TestCase", back_populates="task", cascade="all, delete-orphan", order_by="TestCase.order_index")
    submissions: Mapped[List["CodingSubmission"]] = relationship("CodingSubmission", back_populates="task", cascade="all, delete-orphan")


class TestCase(Base, TimestampMixin):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("coding_tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    task: Mapped["CodingTask"] = relationship("CodingTask", back_populates="test_cases")


class CodingSubmission(Base, TimestampMixin):
    __tablename__ = "coding_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("coding_tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # accepted, wrong_answer, runtime_error, timeout, forbidden_syntax
    passed_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="coding_submissions")
    task: Mapped["CodingTask"] = relationship("CodingTask", back_populates="submissions")

    __table_args__ = (
        Index("idx_coding_submissions_user_task", "user_id", "task_id"),
    )
