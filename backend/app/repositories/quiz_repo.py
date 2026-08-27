from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload
from app.models.quiz import Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer
from app.repositories.base import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(Quiz, session)

    async def get_by_id_with_questions(self, quiz_id: int) -> Optional[Quiz]:
        result = await self.session.execute(
            select(Quiz)
            .options(
                selectinload(Quiz.questions).selectinload(Question.options)
            )
            .where(Quiz.id == quiz_id)
        )
        return result.scalars().first()

    async def list_by_topic(self, topic_id: int) -> List[Quiz]:
        result = await self.session.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.topic_id == topic_id, Quiz.is_published == True)
        )
        return list(result.scalars().all())

    async def list_all_active(self, quiz_type: Optional[str] = None) -> List[Quiz]:
        query = select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.is_published == True)
        if quiz_type:
            query = query.where(Quiz.quiz_type == quiz_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save_attempt(
        self,
        user_id: int,
        quiz_id: int,
        score: int,
        max_score: int,
        percentage: float,
        passed: bool,
        time_spent_seconds: int,
    ) -> QuizAttempt:
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            max_score=max_score,
            percentage=percentage,
            passed=passed,
            time_spent_seconds=time_spent_seconds,
            completed_at=datetime.now(timezone.utc)
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def save_answers(self, answers: List[QuizAnswer]):
        self.session.add_all(answers)
        await self.session.flush()

    async def get_user_attempts_for_quiz(self, user_id: int, quiz_id: int) -> List[QuizAttempt]:
        result = await self.session.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id, QuizAttempt.quiz_id == quiz_id)
            .order_by(QuizAttempt.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_best_scores(self, user_id: int) -> dict:
        result = await self.session.execute(
            select(
                QuizAttempt.quiz_id,
                func.max(QuizAttempt.score).label("best_score"),
                func.max(case((QuizAttempt.passed == True, 1), else_=0)).label("is_passed_int")
            )
            .where(QuizAttempt.user_id == user_id)
            .group_by(QuizAttempt.quiz_id)
        )
        scores = {}
        for row in result.all():
            scores[row.quiz_id] = {
                "best_score": row.best_score,
                "is_passed": bool(row.is_passed_int)
            }
        return scores

    async def get_recent_mistake_questions(self, user_id: int, limit: int = 10) -> List[Question]:
        # Fetch questions where user made mistakes and hasn't resolved them
        from app.models.analytics import MistakeLog
        result = await self.session.execute(
            select(Question)
            .join(MistakeLog, MistakeLog.question_id == Question.id)
            .options(selectinload(Question.options))
            .where(MistakeLog.user_id == user_id, MistakeLog.is_resolved == False)
            .order_by(MistakeLog.last_mistake_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
