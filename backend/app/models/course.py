from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), default="book", nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="course", cascade="all, delete-orphan", order_by="Topic.order_index")
    translations: Mapped[List["CourseTranslation"]] = relationship("CourseTranslation", back_populates="course", cascade="all, delete-orphan")


class Topic(Base, TimestampMixin):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), default="folder", nullable=True)
    color_accent: Mapped[str] = mapped_column(String(50), default="blue", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    est_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    course: Mapped["Course"] = relationship("Course", back_populates="topics")
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="topic", cascade="all, delete-orphan", order_by="Lesson.order_index")
    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")
    coding_tasks: Mapped[List["CodingTask"]] = relationship("CodingTask", back_populates="topic", cascade="all, delete-orphan")
    masteries: Mapped[List["TopicMastery"]] = relationship("TopicMastery", back_populates="topic", cascade="all, delete-orphan")
    translations: Mapped[List["TopicTranslation"]] = relationship("TopicTranslation", back_populates="topic", cascade="all, delete-orphan")


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")
    progress_records: Mapped[List["LessonProgress"]] = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    translations: Mapped[List["LessonTranslation"]] = relationship("LessonTranslation", back_populates="lesson", cascade="all, delete-orphan")


class CourseTranslation(Base, TimestampMixin):
    __tablename__ = "course_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    course: Mapped["Course"] = relationship("Course", back_populates="translations")

    __table_args__ = (UniqueConstraint("course_id", "locale", name="uq_course_translation_locale"),)


class TopicTranslation(Base, TimestampMixin):
    __tablename__ = "topic_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="translations")

    __table_args__ = (UniqueConstraint("topic_id", "locale", name="uq_topic_translation_locale"),)


class LessonTranslation(Base, TimestampMixin):
    __tablename__ = "lesson_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="translations")

    __table_args__ = (UniqueConstraint("lesson_id", "locale", name="uq_lesson_translation_locale"),)


class LessonProgress(Base, TimestampMixin):
    __tablename__ = "lesson_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress_records")

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )


class StudySession(Base, TimestampMixin):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), default="quiz", nullable=False)
