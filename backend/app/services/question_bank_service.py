import hashlib
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from app.models.specification import Subject, SpecificationTopic, SpecificationSection
from app.models.question_bank import (
    BankQuestion, QuestionVersion, QuestionTranslation, QuestionBankOption,
    QuestionBankOptionTranslation, QuestionProvenance, BankSolution,
    BankSolutionTranslation, Tag, QuestionTag, QuestionDifficulty, OfficialStatus
)


class QuestionBankService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_questions(
        self,
        subject_code: str = "informatics",
        section_id: Optional[int] = None,
        topic_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        year: Optional[int] = None,
        question_type: Optional[str] = None,
        official_status: Optional[str] = None,
        locale: str = "kk",
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieves paginated questions matching multi-criteria filters with localized content.
        """
        limit = min(max(1, limit), 100)

        # Base query joining subject and translations
        stmt = (
            select(BankQuestion)
            .join(Subject, BankQuestion.subject_id == Subject.id)
            .where(Subject.code == subject_code)
            .where(BankQuestion.is_active == True)
        )

        if difficulty:
            stmt = stmt.where(BankQuestion.difficulty == difficulty.upper())
        if year:
            stmt = stmt.where(BankQuestion.year == year)
        if question_type:
            stmt = stmt.where(BankQuestion.question_type == question_type)
        if official_status:
            stmt = stmt.where(BankQuestion.official_status == official_status)
        if topic_id:
            stmt = stmt.where(BankQuestion.specification_topic_id == topic_id)

        # Search query filter on translations
        if search_query and search_query.strip():
            term = f"%{search_query.strip()}%"
            stmt = stmt.join(QuestionTranslation, BankQuestion.id == QuestionTranslation.question_id).where(
                or_(
                    QuestionTranslation.text.ilike(term),
                    QuestionTranslation.explanation.ilike(term)
                )
            )

        # Count total matching
        subq = stmt.with_only_columns(BankQuestion.id).order_by(None).subquery()
        count_stmt = select(func.count()).select_from(subq)
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Eager load translations, options, and provenance
        stmt = (
            stmt.options(
                selectinload(BankQuestion.translations),
                selectinload(BankQuestion.options).selectinload(QuestionBankOption.translations),
                selectinload(BankQuestion.provenance_records),
                selectinload(BankQuestion.specification_topic),
            )
            .order_by(BankQuestion.year.desc(), BankQuestion.id.asc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        questions = result.scalars().unique().all()

        output = []
        for q in questions:
            # Match translation for requested locale or fallback to original language
            translation = next((t for t in q.translations if t.locale == locale), None)
            if not translation:
                translation = next((t for t in q.translations if t.locale == q.original_language), None)
            if not translation and q.translations:
                translation = q.translations[0]

            # Options
            options_data = []
            for opt in q.options:
                opt_trans = next((ot for ot in opt.translations if ot.locale == locale), None)
                if not opt_trans:
                    opt_trans = next((ot for ot in opt.translations if ot.locale == q.original_language), None)
                if not opt_trans and opt.translations:
                    opt_trans = opt.translations[0]

                options_data.append({
                    "id": opt.id,
                    "option_key": opt.option_key,
                    "text": opt_trans.text if opt_trans else "",
                    "is_correct": opt.is_correct,
                    "order_index": opt.order_index,
                })

            # Provenance
            provenance_list = [
                {
                    "source_title": prov.source_title,
                    "source_url": prov.source_url,
                    "official_status": prov.official_status,
                    "license_type": prov.license_type,
                    "reuse_allowed": prov.reuse_allowed,
                    "retrieved_at": prov.retrieved_at.isoformat() if prov.retrieved_at else None,
                }
                for prov in q.provenance_records
            ]

            output.append({
                "id": q.id,
                "uuid": q.uuid_str,
                "text": translation.text if translation else "",
                "code_snippet": translation.code_snippet if translation else None,
                "explanation": translation.explanation if translation else None,
                "locale": translation.locale if translation else locale,
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "difficulty_score": q.difficulty_score,
                "official_status": q.official_status,
                "year": q.year,
                "maximum_score": q.maximum_score,
                "estimated_time_seconds": q.estimated_time_seconds,
                "topic_title": q.specification_topic.title_kk if (q.specification_topic and locale == "kk") else (q.specification_topic.title_ru if q.specification_topic else None),
                "options": options_data,
                "provenance": provenance_list,
            })

        return output, total

    async def get_question_by_id(self, question_id: int, locale: str = "kk") -> Optional[Dict[str, Any]]:
        """
        Fetches a single question with complete details, options, step-by-step solution, and provenance.
        """
        stmt = (
            select(BankQuestion)
            .options(
                selectinload(BankQuestion.translations),
                selectinload(BankQuestion.options).selectinload(QuestionBankOption.translations),
                selectinload(BankQuestion.solutions).selectinload(BankSolution.translations),
                selectinload(BankQuestion.provenance_records),
                selectinload(BankQuestion.specification_topic),
            )
            .where(BankQuestion.id == question_id)
        )
        result = await self.session.execute(stmt)
        q = result.scalars().first()
        if not q:
            return None

        # Pick translation
        translation = next((t for t in q.translations if t.locale == locale), None)
        if not translation:
            translation = next((t for t in q.translations if t.locale == q.original_language), None)
        if not translation and q.translations:
            translation = q.translations[0]

        # Options
        options_data = []
        for opt in q.options:
            opt_trans = next((ot for ot in opt.translations if ot.locale == locale), None)
            if not opt_trans and opt.translations:
                opt_trans = opt.translations[0]

            options_data.append({
                "id": opt.id,
                "option_key": opt.option_key,
                "text": opt_trans.text if opt_trans else "",
                "is_correct": opt.is_correct,
                "order_index": opt.order_index,
            })

        # Solutions
        solutions_data = []
        for sol in q.solutions:
            sol_trans = next((st for st in sol.translations if st.locale == locale), None)
            if not sol_trans and sol.translations:
                sol_trans = sol.translations[0]

            solutions_data.append({
                "approach_type": sol.approach_type,
                "complexity": sol.complexity,
                "step_by_step_explanation": sol_trans.step_by_step_explanation if sol_trans else "",
                "exam_tip": sol_trans.exam_tip if sol_trans else None,
            })

        # Provenance
        provenance_list = [
            {
                "source_title": prov.source_title,
                "source_url": prov.source_url,
                "official_status": prov.official_status,
                "license_type": prov.license_type,
                "reuse_allowed": prov.reuse_allowed,
                "retrieved_at": prov.retrieved_at.isoformat() if prov.retrieved_at else None,
            }
            for prov in q.provenance_records
        ]

        return {
            "id": q.id,
            "uuid": q.uuid_str,
            "text": translation.text if translation else "",
            "code_snippet": translation.code_snippet if translation else None,
            "explanation": translation.explanation if translation else None,
            "locale": translation.locale if translation else locale,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "difficulty_score": q.difficulty_score,
            "official_status": q.official_status,
            "year": q.year,
            "maximum_score": q.maximum_score,
            "estimated_time_seconds": q.estimated_time_seconds,
            "options": options_data,
            "solutions": solutions_data,
            "provenance": provenance_list,
        }
