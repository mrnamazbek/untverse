from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.course_repo import CourseRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.services.gamification_service import GamificationService
from app.schemas.course import CourseResponse, TopicResponse, LessonResponse, LessonCompleteResponse
from app.core.exceptions import NotFoundException


class LearningService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.analytics_repo = AnalyticsRepository(session)
        self.gamification_service = GamificationService(session)

    async def get_courses_hierarchy(self, user_id: Optional[int] = None) -> List[CourseResponse]:
        courses = await self.course_repo.get_all_with_topics()
        completed_lesson_ids = set()
        if user_id:
            completed_lesson_ids = set(await self.course_repo.get_user_completed_lesson_ids(user_id))

        res = []
        for c in courses:
            topics_dto = []
            for t in c.topics:
                lessons_dto = []
                for l in t.lessons:
                    lessons_dto.append(LessonResponse(
                        id=l.id,
                        topic_id=l.topic_id,
                        title=l.title,
                        slug=l.slug,
                        content=l.content,
                        summary=l.summary,
                        order_index=l.order_index,
                        xp_reward=l.xp_reward,
                        is_published=l.is_published,
                        is_completed_by_user=(l.id in completed_lesson_ids),
                        created_at=l.created_at
                    ))
                topics_dto.append(TopicResponse(
                    id=t.id,
                    course_id=t.course_id,
                    title=t.title,
                    slug=t.slug,
                    description=t.description,
                    icon=t.icon,
                    color_accent=t.color_accent,
                    order_index=t.order_index,
                    est_minutes=t.est_minutes,
                    xp_reward=t.xp_reward,
                    lessons_count=len(t.lessons),
                    lessons=lessons_dto
                ))
            res.append(CourseResponse(
                id=c.id,
                title=c.title,
                slug=c.slug,
                description=c.description,
                icon=c.icon,
                is_published=c.is_published,
                order_index=c.order_index,
                topics=topics_dto,
                created_at=c.created_at
            ))
        return res

    async def get_topic_detail(self, slug: str, user_id: Optional[int] = None) -> TopicResponse:
        topic = await self.course_repo.get_topic_by_slug(slug)
        if not topic:
            raise NotFoundException(detail=f"Тема '{slug}' не найдена")

        completed_lesson_ids = set()
        if user_id:
            completed_lesson_ids = set(await self.course_repo.get_user_completed_lesson_ids(user_id))

        lessons_dto = [
            LessonResponse(
                id=l.id,
                topic_id=l.topic_id,
                title=l.title,
                slug=l.slug,
                content=l.content,
                summary=l.summary,
                order_index=l.order_index,
                xp_reward=l.xp_reward,
                is_published=l.is_published,
                is_completed_by_user=(l.id in completed_lesson_ids),
                created_at=l.created_at
            ) for l in topic.lessons
        ]

        return TopicResponse(
            id=topic.id,
            course_id=topic.course_id,
            title=topic.title,
            slug=topic.slug,
            description=topic.description,
            icon=topic.icon,
            color_accent=topic.color_accent,
            order_index=topic.order_index,
            est_minutes=topic.est_minutes,
            xp_reward=topic.xp_reward,
            lessons_count=len(topic.lessons),
            quizzes_count=len(topic.quizzes),
            coding_tasks_count=len(topic.coding_tasks),
            lessons=lessons_dto
        )

    async def get_lesson_detail(self, lesson_id: int, user_id: Optional[int] = None) -> LessonResponse:
        lesson = await self.course_repo.get_lesson_by_id(lesson_id)
        if not lesson:
            raise NotFoundException(detail=f"Урок ID {lesson_id} не найден")

        is_completed = False
        if user_id:
            completed_ids = await self.course_repo.get_user_completed_lesson_ids(user_id)
            is_completed = lesson.id in completed_ids

        return LessonResponse(
            id=lesson.id,
            topic_id=lesson.topic_id,
            title=lesson.title,
            slug=lesson.slug,
            content=lesson.content,
            summary=lesson.summary,
            order_index=lesson.order_index,
            xp_reward=lesson.xp_reward,
            is_published=lesson.is_published,
            is_completed_by_user=is_completed,
            created_at=lesson.created_at
        )

    async def complete_lesson(self, user_id: int, lesson_id: int) -> LessonCompleteResponse:
        lesson = await self.course_repo.get_lesson_by_id(lesson_id)
        if not lesson:
            raise NotFoundException(detail=f"Урок ID {lesson_id} не найден")

        completed_ids = await self.course_repo.get_user_completed_lesson_ids(user_id)
        is_already_completed = lesson.id in completed_ids

        await self.course_repo.mark_lesson_completed(user_id, lesson_id)
        await self.analytics_repo.record_study_session(user_id, 300, activity_type="lesson")

        if not is_already_completed:
            new_total_xp, new_level, leveled_up = await self.gamification_service.handle_lesson_completed(
                user_id=user_id,
                lesson_id=lesson_id,
                xp_reward=lesson.xp_reward
            )
            xp_earned = lesson.xp_reward
        else:
            profile = (await self.gamification_service.user_repo.get_with_profile(user_id)).profile
            new_total_xp = profile.total_xp
            new_level = profile.current_level
            leveled_up = False
            xp_earned = 0

        return LessonCompleteResponse(
            lesson_id=lesson.id,
            is_completed=True,
            xp_earned=xp_earned,
            new_total_xp=new_total_xp,
            new_level=new_level,
            leveled_up=leveled_up
        )
