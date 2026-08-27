from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.course import Course, Topic, Lesson, LessonProgress
from app.models.quiz import Quiz
from app.models.coding import CodingTask
from app.models.analytics import TopicMastery
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_all_with_topics(self) -> List[Course]:
        result = await self.session.execute(
            select(Course)
            .options(
                selectinload(Course.translations),
                selectinload(Course.topics).selectinload(Topic.translations),
                selectinload(Course.topics).selectinload(Topic.lessons).selectinload(Lesson.translations),
                selectinload(Course.topics).selectinload(Topic.quizzes),
                selectinload(Course.topics).selectinload(Topic.coding_tasks),
            )
            .order_by(Course.order_index)
        )
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[Course]:
        result = await self.session.execute(
            select(Course)
            .options(
                selectinload(Course.translations),
                selectinload(Course.topics).selectinload(Topic.translations),
                selectinload(Course.topics).selectinload(Topic.lessons).selectinload(Lesson.translations),
                selectinload(Course.topics).selectinload(Topic.quizzes),
                selectinload(Course.topics).selectinload(Topic.coding_tasks),
            )
            .where(Course.slug == slug)
        )
        return result.scalars().first()

    async def get_topic_by_slug(self, slug: str) -> Optional[Topic]:
        result = await self.session.execute(
            select(Topic)
            .options(
                selectinload(Topic.translations),
                selectinload(Topic.lessons).selectinload(Lesson.translations),
                selectinload(Topic.quizzes),
                selectinload(Topic.coding_tasks),
            )
            .where(Topic.slug == slug)
        )
        return result.scalars().first()

    async def get_topic_by_id(self, topic_id: int) -> Optional[Topic]:
        result = await self.session.execute(
            select(Topic)
            .options(
                selectinload(Topic.translations),
                selectinload(Topic.lessons).selectinload(Lesson.translations),
                selectinload(Topic.quizzes),
                selectinload(Topic.coding_tasks),
            )
            .where(Topic.id == topic_id)
        )
        return result.scalars().first()

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        result = await self.session.execute(
            select(Lesson)
            .options(selectinload(Lesson.topic), selectinload(Lesson.translations))
            .where(Lesson.id == lesson_id)
        )
        return result.scalars().first()

    async def mark_lesson_completed(self, user_id: int, lesson_id: int) -> LessonProgress:
        result = await self.session.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id == lesson_id
            )
        )
        progress = result.scalars().first()
        if not progress:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=datetime.now(timezone.utc)
            )
            self.session.add(progress)
            await self.session.flush()
        return progress

    async def get_user_completed_lesson_ids(self, user_id: int) -> List[int]:
        result = await self.session.execute(
            select(LessonProgress.lesson_id).where(
                LessonProgress.user_id == user_id,
                LessonProgress.is_completed == True
            )
        )
        return list(result.scalars().all())
