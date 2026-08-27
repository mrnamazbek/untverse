from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.repositories.analytics_repo import AnalyticsRepository
from app.repositories.quiz_repo import QuizRepository
from app.repositories.user_repo import UserRepository
from app.models.user import User, UserProfile
from app.models.quiz import Question, QuizAttempt, QuizAnswer
from app.schemas.analytics import (
    StudentAnalyticsDashboard, MistakeItem, SpacedCardReviewItem, SpacedReviewSubmit
)


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics_repo = AnalyticsRepository(session)
        self.quiz_repo = QuizRepository(session)
        self.user_repo = UserRepository(session)

    async def get_student_dashboard(self, user_id: int) -> StudentAnalyticsDashboard:
        data = await self.analytics_repo.get_student_dashboard_metrics(user_id)
        return StudentAnalyticsDashboard(**data)

    async def get_unresolved_mistakes(self, user_id: int) -> List[MistakeItem]:
        mistakes = await self.analytics_repo.get_unresolved_mistakes(user_id)
        return [MistakeItem(**m) for m in mistakes]

    async def get_due_spaced_repetition_cards(self, user_id: int) -> List[SpacedCardReviewItem]:
        cards = await self.analytics_repo.get_due_srs_cards(user_id)
        return [SpacedCardReviewItem(**c) for c in cards]

    async def submit_spaced_review(self, user_id: int, submit: SpacedReviewSubmit) -> Dict[str, Any]:
        card = await self.analytics_repo.update_srs_card_review(submit.card_id, submit.rating)
        
        # If rating was high (>=4), also mark mistake log as resolved
        if submit.rating >= 4:
            await self.analytics_repo.resolve_mistake(user_id, card.question_id)

        return {
            "card_id": card.id,
            "next_review_at": card.next_review_at,
            "interval_days": card.interval_days,
            "ease_factor": card.ease_factor
        }

    async def get_teacher_class_analytics(self) -> Dict[str, Any]:
        """
        Aggregated statistics for instructors and administrators.
        """
        total_students_res = await self.session.execute(
            select(func.count(User.id)).where(User.role == "student")
        )
        total_students = total_students_res.scalar() or 0

        avg_xp_res = await self.session.execute(
            select(func.coalesce(func.avg(UserProfile.total_xp), 0))
        )
        avg_xp = int(avg_xp_res.scalar() or 0)

        total_quizzes_res = await self.session.execute(
            select(func.count(QuizAttempt.id))
        )
        total_attempts = total_quizzes_res.scalar() or 0

        avg_score_res = await self.session.execute(
            select(func.coalesce(func.avg(QuizAttempt.percentage), 0.0))
        )
        avg_score = round(float(avg_score_res.scalar() or 0.0), 1)

        # Most difficult questions (lowest accuracy)
        hard_questions_res = await self.session.execute(
            select(
                Question.id,
                Question.text,
                func.count(QuizAnswer.id).label("total_answers"),
                func.sum(case((QuizAnswer.is_correct == True, 1), else_=0)).label("correct_answers")
            )
            .join(QuizAnswer, QuizAnswer.question_id == Question.id)
            .group_by(Question.id)
            .having(func.count(QuizAnswer.id) >= 2)
            .order_by((func.sum(case((QuizAnswer.is_correct == True, 1), else_=0)) * 1.0 / func.count(QuizAnswer.id)).asc())
            .limit(5)
        )
        hard_questions = []
        for row in hard_questions_res.all():
            total = row.total_answers
            correct = row.correct_answers or 0
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
            hard_questions.append({
                "question_id": row.id,
                "question_text": row.text,
                "accuracy_percentage": accuracy,
                "total_attempts": total
            })

        return {
            "total_students": total_students,
            "average_student_xp": avg_xp,
            "total_quiz_attempts": total_attempts,
            "overall_accuracy_percentage": avg_score,
            "most_difficult_questions": hard_questions
        }
