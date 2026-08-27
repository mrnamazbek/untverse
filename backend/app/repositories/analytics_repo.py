from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import selectinload
from app.models.analytics import TopicMastery, MistakeLog, SpacedRepetitionCard
from app.models.course import Topic, StudySession
from app.models.quiz import Question, QuizAttempt, QuizAnswer
from app.models.coding import CodingSubmission


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_topic_mastery(self, user_id: int, topic_id: int, is_correct: bool):
        res = await self.session.execute(
            select(TopicMastery).where(
                TopicMastery.user_id == user_id,
                TopicMastery.topic_id == topic_id
            )
        )
        tm = res.scalars().first()
        if not tm:
            tm = TopicMastery(
                user_id=user_id,
                topic_id=topic_id,
                total_answered=1,
                correct_count=1 if is_correct else 0,
                mastery_percentage=100.0 if is_correct else 0.0,
                last_evaluated_at=datetime.now(timezone.utc)
            )
            self.session.add(tm)
        else:
            tm.total_answered += 1
            if is_correct:
                tm.correct_count += 1
            tm.mastery_percentage = round((tm.correct_count / tm.total_answered) * 100, 1)
            tm.last_evaluated_at = datetime.now(timezone.utc)

        await self.session.flush()
        return tm

    async def get_user_masteries(self, user_id: int) -> List[dict]:
        topics_res = await self.session.execute(select(Topic).order_by(Topic.order_index))
        topics = topics_res.scalars().all()

        tm_res = await self.session.execute(
            select(TopicMastery).where(TopicMastery.user_id == user_id)
        )
        tm_map = {m.topic_id: m for m in tm_res.scalars().all()}

        output = []
        for t in topics:
            m = tm_map.get(t.id)
            output.append({
                "topic_id": t.id,
                "topic_title": t.title,
                "topic_slug": t.slug,
                "color_accent": t.color_accent,
                "mastery_percentage": m.mastery_percentage if m else 0.0,
                "total_answered": m.total_answered if m else 0,
                "correct_count": m.correct_count if m else 0,
            })
        return output

    async def record_mistake(self, user_id: int, question_id: int):
        res = await self.session.execute(
            select(MistakeLog).where(
                MistakeLog.user_id == user_id,
                MistakeLog.question_id == question_id
            )
        )
        log = res.scalars().first()
        if not log:
            log = MistakeLog(
                user_id=user_id,
                question_id=question_id,
                error_count=1,
                is_resolved=False,
                last_mistake_at=datetime.now(timezone.utc)
            )
            self.session.add(log)
        else:
            log.error_count += 1
            log.is_resolved = False
            log.last_mistake_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def resolve_mistake(self, user_id: int, question_id: int):
        res = await self.session.execute(
            select(MistakeLog).where(
                MistakeLog.user_id == user_id,
                MistakeLog.question_id == question_id
            )
        )
        log = res.scalars().first()
        if log:
            log.is_resolved = True
            await self.session.flush()

    async def get_unresolved_mistakes(self, user_id: int) -> List[dict]:
        res = await self.session.execute(
            select(MistakeLog)
            .options(selectinload(MistakeLog.question))
            .where(MistakeLog.user_id == user_id, MistakeLog.is_resolved == False)
            .order_by(MistakeLog.error_count.desc(), MistakeLog.last_mistake_at.desc())
        )
        logs = res.scalars().all()
        output = []
        for log in logs:
            q = log.question
            output.append({
                "id": log.id,
                "question_id": q.id,
                "question_text": q.text,
                "question_type": q.question_type,
                "code_snippet": q.code_snippet,
                "explanation": q.explanation,
                "error_count": log.error_count,
                "is_resolved": log.is_resolved,
                "last_mistake_at": log.last_mistake_at
            })
        return output

    async def get_or_create_srs_card(self, user_id: int, question_id: int) -> SpacedRepetitionCard:
        res = await self.session.execute(
            select(SpacedRepetitionCard).where(
                SpacedRepetitionCard.user_id == user_id,
                SpacedRepetitionCard.question_id == question_id
            )
        )
        card = res.scalars().first()
        if not card:
            card = SpacedRepetitionCard(
                user_id=user_id,
                question_id=question_id,
                repetition_number=0,
                interval_days=1,
                ease_factor=2.5,
                next_review_at=datetime.now(timezone.utc),
            )
            self.session.add(card)
            await self.session.flush()
        return card

    async def get_due_srs_cards(self, user_id: int, limit: int = 20) -> List[dict]:
        now = datetime.now(timezone.utc)
        res = await self.session.execute(
            select(SpacedRepetitionCard)
            .options(
                selectinload(SpacedRepetitionCard.question).selectinload(Question.options)
            )
            .where(
                SpacedRepetitionCard.user_id == user_id,
                SpacedRepetitionCard.next_review_at <= now
            )
            .order_by(SpacedRepetitionCard.next_review_at.asc())
            .limit(limit)
        )
        cards = res.scalars().all()
        output = []
        for c in cards:
            q = c.question
            options = [{"id": o.id, "text": o.text} for o in q.options] if q.options else []
            output.append({
                "card_id": c.id,
                "question_id": q.id,
                "question_text": q.text,
                "code_snippet": q.code_snippet,
                "question_type": q.question_type,
                "interval_days": c.interval_days,
                "repetition_number": c.repetition_number,
                "options": options
            })
        return output

    async def update_srs_card_review(self, card_id: int, rating: int) -> SpacedRepetitionCard:
        """
        SuperMemo-2 calculation:
        rating: 0-5
        EF' = EF + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
        """
        res = await self.session.execute(
            select(SpacedRepetitionCard).where(SpacedRepetitionCard.id == card_id)
        )
        card = res.scalars().first()
        if not card:
            raise ValueError(f"Card {card_id} not found")

        now = datetime.now(timezone.utc)
        card.last_reviewed_at = now

        if rating < 3:
            # Failed recall, reset repetition
            card.repetition_number = 0
            card.interval_days = 1
        else:
            # Successful recall
            if card.repetition_number == 0:
                card.interval_days = 1
            elif card.repetition_number == 1:
                card.interval_days = 6
            else:
                card.interval_days = int(round(card.interval_days * card.ease_factor))
            card.repetition_number += 1

        # Adjust ease factor
        new_ef = card.ease_factor + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
        card.ease_factor = max(1.3, round(new_ef, 2))
        card.next_review_at = now + timedelta(days=card.interval_days)

        await self.session.flush()
        return card

    async def record_study_session(self, user_id: int, duration_seconds: int, activity_type: str):
        session = StudySession(
            user_id=user_id,
            duration_seconds=duration_seconds,
            activity_type=activity_type
        )
        self.session.add(session)
        await self.session.flush()

    async def get_student_dashboard_metrics(self, user_id: int) -> dict:
        # Total study time
        study_time_res = await self.session.execute(
            select(func.coalesce(func.sum(StudySession.duration_seconds), 0))
            .where(StudySession.user_id == user_id)
        )
        total_seconds = study_time_res.scalar() or 0
        total_minutes = total_seconds // 60

        # Quizzes count & average score
        quizzes_res = await self.session.execute(
            select(
                func.count(QuizAttempt.id),
                func.coalesce(func.avg(QuizAttempt.percentage), 0.0)
            ).where(QuizAttempt.user_id == user_id)
        )
        q_row = quizzes_res.first()
        quizzes_count = q_row[0] if q_row else 0
        avg_accuracy = round(float(q_row[1]), 1) if q_row else 0.0

        # Coding tasks solved
        coding_res = await self.session.execute(
            select(func.count(func.distinct(CodingSubmission.task_id)))
            .where(CodingSubmission.user_id == user_id, CodingSubmission.status == "accepted")
        )
        solved_tasks = coding_res.scalar() or 0

        # Unresolved mistakes count
        mistakes_res = await self.session.execute(
            select(func.count(MistakeLog.id))
            .where(MistakeLog.user_id == user_id, MistakeLog.is_resolved == False)
        )
        unresolved_mistakes = mistakes_res.scalar() or 0

        # Due SRS cards count
        now = datetime.now(timezone.utc)
        due_res = await self.session.execute(
            select(func.count(SpacedRepetitionCard.id))
            .where(SpacedRepetitionCard.user_id == user_id, SpacedRepetitionCard.next_review_at <= now)
        )
        due_reviews = due_res.scalar() or 0

        # Masteries
        all_masteries = await self.get_user_masteries(user_id)
        sorted_by_mastery = sorted(all_masteries, key=lambda x: x["mastery_percentage"], reverse=True)
        strongest = sorted_by_mastery[:3] if sorted_by_mastery else []
        weakest = sorted([m for m in all_masteries if m["total_answered"] > 0], key=lambda x: x["mastery_percentage"])[:3]

        # Calculate overall UNT readiness score
        # Formula: (avg_accuracy * 0.4) + (topic_mastery_avg * 0.4) + (min(100, solved_tasks * 20) * 0.2)
        avg_mastery = sum(m["mastery_percentage"] for m in all_masteries) / max(1, len(all_masteries))
        task_component = min(100, solved_tasks * 20)
        readiness = int(round((avg_accuracy * 0.4) + (avg_mastery * 0.4) + (task_component * 0.2)))
        readiness = max(0, min(100, readiness))

        return {
            "total_study_time_minutes": total_minutes,
            "unt_readiness_score": readiness,
            "quizzes_completed_count": quizzes_count,
            "coding_tasks_solved_count": solved_tasks,
            "average_quiz_accuracy": avg_accuracy,
            "strongest_topics": strongest,
            "weakest_topics": weakest,
            "all_topic_masteries": all_masteries,
            "unresolved_mistakes_count": unresolved_mistakes,
            "due_reviews_count": due_reviews,
            "recent_activity_days": [
                {"date": (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 5 + (i % 4) * 3}
                for i in range(7)
            ]
        }
