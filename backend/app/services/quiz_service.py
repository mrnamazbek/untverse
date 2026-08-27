from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.quiz_repo import QuizRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.services.gamification_service import GamificationService
from app.models.quiz import Quiz, Question, QuizAttempt, QuizAnswer
from app.core.events import QuizCompletedEvent
from app.schemas.quiz import (
    QuizResponse, QuizListItem, QuestionResponse, QuestionOptionResponse,
    QuizSubmitRequest, QuizSubmitResponse, AnswerReview
)
from app.core.exceptions import NotFoundException, BadRequestException


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.quiz_repo = QuizRepository(session)
        self.analytics_repo = AnalyticsRepository(session)
        self.gamification_service = GamificationService(session)

    async def list_quizzes(self, user_id: Optional[int] = None, quiz_type: Optional[str] = None) -> List[QuizListItem]:
        quizzes = await self.quiz_repo.list_all_active(quiz_type)
        user_scores = {}
        if user_id:
            user_scores = await self.quiz_repo.get_user_best_scores(user_id)

        output = []
        for q in quizzes:
            user_stat = user_scores.get(q.id, {})
            output.append(QuizListItem(
                id=q.id,
                topic_id=q.topic_id,
                title=q.title,
                description=q.description,
                quiz_type=q.quiz_type,
                time_limit_seconds=q.time_limit_seconds,
                passing_score=q.passing_score,
                xp_reward=q.xp_reward,
                is_published=q.is_published,
                questions_count=len(q.questions),
                user_best_score=user_stat.get("best_score"),
                user_completed=user_stat.get("is_passed", False)
            ))
        return output

    async def get_quiz_for_student(self, quiz_id: int) -> QuizResponse:
        quiz = await self.quiz_repo.get_by_id_with_questions(quiz_id)
        if not quiz:
            raise NotFoundException(detail=f"Тест ID {quiz_id} не найден")

        questions_dto = []
        for q in quiz.questions:
            options_dto = [
                QuestionOptionResponse(
                    id=opt.id,
                    text=opt.text,
                    order_index=opt.order_index
                ) for opt in q.options
            ]
            questions_dto.append(QuestionResponse(
                id=q.id,
                quiz_id=q.quiz_id,
                text=q.text,
                code_snippet=q.code_snippet,
                question_type=q.question_type,
                difficulty=q.difficulty,
                points=q.points,
                order_index=q.order_index,
                extra_data=q.extra_data,
                options=options_dto
            ))

        return QuizResponse(
            id=quiz.id,
            topic_id=quiz.topic_id,
            title=quiz.title,
            description=quiz.description,
            quiz_type=quiz.quiz_type,
            time_limit_seconds=quiz.time_limit_seconds,
            passing_score=quiz.passing_score,
            xp_reward=quiz.xp_reward,
            is_published=quiz.is_published,
            questions=questions_dto
        )

    async def submit_quiz(self, user_id: int, quiz_id: int, request: QuizSubmitRequest) -> QuizSubmitResponse:
        quiz = await self.quiz_repo.get_by_id_with_questions(quiz_id)
        if not quiz:
            raise NotFoundException(detail=f"Тест ID {quiz_id} не найден")

        # Map questions by ID
        q_map: Dict[int, Question] = {q.id: q for q in quiz.questions}

        total_points = sum(q.points for q in quiz.questions)
        earned_points = 0
        correct_count = 0
        answers_review: List[AnswerReview] = []
        quiz_answers_to_save: List[QuizAnswer] = []

        for user_ans in request.answers:
            question = q_map.get(user_ans.question_id)
            if not question:
                continue

            # Identify correct option IDs
            correct_opt_ids = [opt.id for opt in question.options if opt.is_correct]
            selected_opt_ids = user_ans.selected_option_ids or []
            
            is_correct = False
            points_awarded = 0

            if question.question_type in ("single_choice", "true_false"):
                if len(selected_opt_ids) == 1 and len(correct_opt_ids) == 1 and selected_opt_ids[0] == correct_opt_ids[0]:
                    is_correct = True
                    points_awarded = question.points
            elif question.question_type == "multiple_choice":
                if set(selected_opt_ids) == set(correct_opt_ids):
                    is_correct = True
                    points_awarded = question.points
            elif question.question_type in ("fill_gap", "sql"):
                # Compare text answers
                user_text = (user_ans.text_answer or "").strip().lower()
                # Correct text options from question options text
                correct_texts = [opt.text.strip().lower() for opt in question.options if opt.is_correct]
                if user_text in correct_texts:
                    is_correct = True
                    points_awarded = question.points
            elif question.question_type == "matching":
                # Matches checked against extra_data or correct option mapping
                if set(selected_opt_ids) == set(correct_opt_ids):
                    is_correct = True
                    points_awarded = question.points

            if is_correct:
                earned_points += points_awarded
                correct_count += 1
                await self.analytics_repo.resolve_mistake(user_id, question.id)
            else:
                # Log mistake for Spaced Repetition and Mistake Workout
                await self.analytics_repo.record_mistake(user_id, question.id)
                await self.analytics_repo.get_or_create_srs_card(user_id, question.id)

            # Update Topic Mastery if topic is linked
            if quiz.topic_id:
                await self.analytics_repo.update_topic_mastery(user_id, quiz.topic_id, is_correct)

            answers_review.append(AnswerReview(
                question_id=question.id,
                question_text=question.text,
                question_type=question.question_type,
                is_correct=is_correct,
                points_awarded=points_awarded,
                max_points=question.points,
                user_selected_options=selected_opt_ids,
                correct_option_ids=correct_opt_ids,
                explanation=question.explanation
            ))

            quiz_answers_to_save.append(QuizAnswer(
                question_id=question.id,
                selected_option_ids=selected_opt_ids,
                text_answer=user_ans.text_answer,
                is_correct=is_correct,
                points_awarded=points_awarded
            ))

        max_score = total_points if total_points > 0 else 1
        percentage = round((earned_points / max_score) * 100, 1)
        passed = percentage >= quiz.passing_score

        # Save Attempt
        attempt = await self.quiz_repo.save_attempt(
            user_id=user_id,
            quiz_id=quiz.id,
            score=earned_points,
            max_score=max_score,
            percentage=percentage,
            passed=passed,
            time_spent_seconds=request.time_spent_seconds,
        )

        for a in quiz_answers_to_save:
            a.attempt_id = attempt.id
        await self.quiz_repo.save_answers(quiz_answers_to_save)

        # Record study session
        await self.analytics_repo.record_study_session(user_id, request.time_spent_seconds, activity_type="quiz")

        # Gamification Event & Rewards
        event = QuizCompletedEvent(
            user_id=user_id,
            quiz_id=quiz.id,
            score=earned_points,
            max_score=max_score,
            percentage=percentage,
            time_spent_seconds=request.time_spent_seconds,
            correct_count=correct_count,
            total_count=len(quiz.questions)
        )
        gamification_rewards = await self.gamification_service.handle_quiz_completed(event)

        return QuizSubmitResponse(
            attempt_id=attempt.id,
            quiz_id=quiz.id,
            score=earned_points,
            max_score=max_score,
            percentage=percentage,
            passed=passed,
            time_spent_seconds=request.time_spent_seconds,
            xp_earned=gamification_rewards["xp_earned"],
            new_total_xp=gamification_rewards["new_total_xp"],
            new_level=gamification_rewards["new_level"],
            leveled_up=gamification_rewards["leveled_up"],
            streak_extended=gamification_rewards["streak_extended"],
            current_streak=gamification_rewards["current_streak"],
            answers_review=answers_review
        )
