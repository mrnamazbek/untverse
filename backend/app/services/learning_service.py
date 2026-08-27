import logging
from typing import Optional, List, Sequence, Tuple, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.course_repo import CourseRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.services.gamification_service import GamificationService
from app.schemas.course import CourseResponse, TopicResponse, LessonResponse, LessonCompleteResponse
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)
SUPPORTED_LOCALES = {"kk", "ru", "en"}
T = TypeVar("T")


class LearningService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.analytics_repo = AnalyticsRepository(session)
        self.gamification_service = GamificationService(session)

    def _translation(self, translations: Sequence[T], locale: str, entity_name: str, entity_id: int) -> Tuple[Optional[T], Optional[str]]:
        """Select the requested translation, then the canonical Russian source.

        A fallback is explicitly represented in every DTO and logged. This
        prevents callers from mistaking a fallback for requested-language data.
        """
        requested = next((translation for translation in translations if getattr(translation, "locale", None) == locale), None)
        if requested:
            return requested, None

        fallback = next((translation for translation in translations if getattr(translation, "locale", None) == "ru"), None)
        logger.warning(
            "Missing %s translation: id=%s requested_locale=%s fallback_locale=%s",
            entity_name,
            entity_id,
            locale,
            "ru" if fallback else "legacy-ru",
        )
        return fallback, "ru"

    def _lesson_response(self, lesson, completed_lesson_ids: set[int], locale: str) -> LessonResponse:
        translation, fallback_locale = self._translation(lesson.translations, locale, "lesson", lesson.id)
        return LessonResponse(
            id=lesson.id,
            topic_id=lesson.topic_id,
            title=translation.title if translation else lesson.title,
            slug=lesson.slug,
            content=translation.content if translation else lesson.content,
            summary=translation.summary if translation else lesson.summary,
            order_index=lesson.order_index,
            xp_reward=lesson.xp_reward,
            is_published=lesson.is_published,
            is_completed_by_user=(lesson.id in completed_lesson_ids),
            created_at=lesson.created_at,
            locale=translation.locale if translation else "ru",
            fallback_locale=fallback_locale,
        )

    def _topic_response(self, topic, completed_lesson_ids: set[int], locale: str) -> TopicResponse:
        translation, fallback_locale = self._translation(topic.translations, locale, "topic", topic.id)
        return TopicResponse(
            id=topic.id,
            course_id=topic.course_id,
            title=translation.title if translation else topic.title,
            slug=topic.slug,
            description=translation.description if translation else topic.description,
            icon=topic.icon,
            color_accent=topic.color_accent,
            order_index=topic.order_index,
            est_minutes=topic.est_minutes,
            xp_reward=topic.xp_reward,
            lessons_count=len(topic.lessons),
            quizzes_count=len(topic.quizzes),
            coding_tasks_count=len(topic.coding_tasks),
            lessons=[self._lesson_response(lesson, completed_lesson_ids, locale) for lesson in topic.lessons],
            locale=translation.locale if translation else "ru",
            fallback_locale=fallback_locale,
        )

    async def get_courses_hierarchy(self, user_id: Optional[int] = None, locale: str = "kk") -> List[CourseResponse]:
        locale = locale if locale in SUPPORTED_LOCALES else "kk"
        courses = await self.course_repo.get_all_with_topics()
        completed_lesson_ids = set()
        if user_id:
            completed_lesson_ids = set(await self.course_repo.get_user_completed_lesson_ids(user_id))

        res = []
        for c in courses:
            topics_dto = []
            for t in c.topics:
                topics_dto.append(self._topic_response(t, completed_lesson_ids, locale))
            translation, fallback_locale = self._translation(c.translations, locale, "course", c.id)
            res.append(CourseResponse(
                id=c.id,
                title=translation.title if translation else c.title,
                slug=c.slug,
                description=translation.description if translation else c.description,
                icon=c.icon,
                is_published=c.is_published,
                order_index=c.order_index,
                topics=topics_dto,
                created_at=c.created_at,
                locale=translation.locale if translation else "ru",
                fallback_locale=fallback_locale,
            ))
        return res

    async def get_topic_detail(self, slug: str, user_id: Optional[int] = None, locale: str = "kk") -> TopicResponse:
        locale = locale if locale in SUPPORTED_LOCALES else "kk"
        topic = await self.course_repo.get_topic_by_slug(slug)
        if not topic:
            raise NotFoundException(detail=f"Тема '{slug}' не найдена")

        completed_lesson_ids = set()
        if user_id:
            completed_lesson_ids = set(await self.course_repo.get_user_completed_lesson_ids(user_id))

        return self._topic_response(topic, completed_lesson_ids, locale)

    async def get_lesson_detail(self, lesson_id: int, user_id: Optional[int] = None, locale: str = "kk") -> LessonResponse:
        locale = locale if locale in SUPPORTED_LOCALES else "kk"
        lesson = await self.course_repo.get_lesson_by_id(lesson_id)
        if not lesson:
            raise NotFoundException(detail=f"Урок ID {lesson_id} не найден")

        is_completed = False
        if user_id:
            completed_ids = await self.course_repo.get_user_completed_lesson_ids(user_id)
            is_completed = lesson.id in completed_ids

        return self._lesson_response(lesson, {lesson.id} if is_completed else set(), locale)

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
