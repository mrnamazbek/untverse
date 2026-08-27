from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Float, JSON, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class QuizType(str, Enum):
    STANDARD = "standard"
    BOSS_CHALLENGE = "boss_challenge"
    RANKED = "ranked"
    UNT_MOCK = "unt_mock"
    DAILY_TRAINING = "daily_training"


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_GAP = "fill_gap"
    SQL = "sql"
    MATCHING = "matching"


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quiz_type: Mapped[str] = mapped_column(String(50), default=QuizType.STANDARD.value, nullable=False, index=True)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=600, nullable=False)
    passing_score: Mapped[int] = mapped_column(Integer, default=70, nullable=False)  # percentage
    xp_reward: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="quizzes")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.order_index")
    attempts: Mapped[List["QuizAttempt"]] = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    code_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    question_type: Mapped[str] = mapped_column(String(50), default=QuestionType.SINGLE_CHOICE.value, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # easy, medium, hard
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # for matching pairs or gap options

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    options: Mapped[List["QuestionOption"]] = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.order_index")
    answers: Mapped[List["QuizAnswer"]] = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")
    mistakes: Mapped[List["MistakeLog"]] = relationship("MistakeLog", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base, TimestampMixin):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question: Mapped["Question"] = relationship("Question", back_populates="options")


class QuizAttempt(Base, TimestampMixin):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
    answers: Mapped[List["QuizAnswer"]] = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_quiz_attempts_user_created", "user_id", "created_at"),
        Index("idx_quiz_attempts_quiz_score", "quiz_id", "score"),
    )


class QuizAnswer(Base, TimestampMixin):
    __tablename__ = "quiz_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    selected_option_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # List[int]
    text_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    attempt: Mapped["QuizAttempt"] = relationship("QuizAttempt", back_populates="answers")
    question: Mapped["Question"] = relationship("Question", back_populates="answers")
