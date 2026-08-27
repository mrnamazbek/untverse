import random
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.question_bank import BankQuestion, QuestionTranslation, QuestionBankOption, QuestionProvenance
from app.models.specification import SpecificationSection, SpecificationTopic


class QuestionSelectionService:
    """
    Scalable question selection engine for student practice and full UNT mocks.
    Avoids expensive `ORDER BY random()` by fetching matching ID primary keys first,
    sampling in memory, and fetching full entities by explicit IN(ids).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def sample_by_topic(
        self,
        specification_topic_id: int,
        count: int = 10,
        difficulty: Optional[str] = None,
        locale: str = "kk"
    ) -> List[Dict[str, Any]]:
        """
        Samples N questions for a specific topic.
        """
        query = select(BankQuestion.id).where(
            BankQuestion.specification_topic_id == specification_topic_id,
            BankQuestion.is_active == True
        )
        if difficulty:
            query = query.where(BankQuestion.difficulty == difficulty.upper())

        res = await self.session.execute(query)
        candidate_ids = [row[0] for row in res.all()]

        if not candidate_ids:
            return []

        sampled_ids = random.sample(candidate_ids, min(count, len(candidate_ids)))
        return await self._fetch_full_questions(sampled_ids, locale)

    async def generate_unt_50_mock(self, locale: str = "kk") -> List[Dict[str, Any]]:
        """
        Generates a balanced 50-question mock exam according to the official NCT specification:
        - Single choice (35 questions)
        - Multiple choice (10 questions)
        - Context / Analytical problem sets (5 questions)
        Distributed across all 6 core domains.
        """
        # Fetch all active question IDs categorized by type
        single_ids_res = await self.session.execute(
            select(BankQuestion.id).where(
                BankQuestion.question_type == "single_choice",
                BankQuestion.is_active == True
            )
        )
        single_ids = [row[0] for row in single_ids_res.all()]

        multi_ids_res = await self.session.execute(
            select(BankQuestion.id).where(
                BankQuestion.question_type == "multiple_choice",
                BankQuestion.is_active == True
            )
        )
        multi_ids = [row[0] for row in multi_ids_res.all()]

        context_ids_res = await self.session.execute(
            select(BankQuestion.id).where(
                BankQuestion.question_type.in_(["context_based", "sql", "python", "matching", "numeric"]),
                BankQuestion.is_active == True
            )
        )
        context_ids = [row[0] for row in context_ids_res.all()]

        # Sample proportions (adjusting to total available pool)
        selected_ids = []
        if single_ids:
            selected_ids.extend(random.sample(single_ids, min(35, len(single_ids))))
        if multi_ids:
            selected_ids.extend(random.sample(multi_ids, min(10, len(multi_ids))))
        if context_ids:
            selected_ids.extend(random.sample(context_ids, min(5, len(context_ids))))

        # If pool is small, fill remaining from overall pool to reach 50 or maximum available
        if len(selected_ids) < 50:
            all_ids_res = await self.session.execute(
                select(BankQuestion.id).where(
                    BankQuestion.is_active == True,
                    ~BankQuestion.id.in_(selected_ids) if selected_ids else True
                )
            )
            remaining_ids = [row[0] for row in all_ids_res.all()]
            needed = 50 - len(selected_ids)
            selected_ids.extend(random.sample(remaining_ids, min(needed, len(remaining_ids))))

        return await self._fetch_full_questions(selected_ids, locale)

    async def _fetch_full_questions(self, question_ids: List[int], locale: str) -> List[Dict[str, Any]]:
        if not question_ids:
            return []

        stmt = (
            select(BankQuestion)
            .options(
                selectinload(BankQuestion.translations),
                selectinload(BankQuestion.options).selectinload(QuestionBankOption.translations),
                selectinload(BankQuestion.provenance_records),
                selectinload(BankQuestion.specification_topic),
            )
            .where(BankQuestion.id.in_(question_ids))
        )
        result = await self.session.execute(stmt)
        questions = result.scalars().unique().all()

        output = []
        for q in questions:
            translation = next((t for t in q.translations if t.locale == locale), None)
            if not translation and q.translations:
                translation = q.translations[0]

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

            output.append({
                "id": q.id,
                "uuid": q.uuid_str,
                "text": translation.text if translation else "",
                "code_snippet": translation.code_snippet if translation else None,
                "explanation": translation.explanation if translation else None,
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "year": q.year,
                "maximum_score": q.maximum_score,
                "options": options_data,
                "provenance": [
                    {
                        "source_title": p.source_title,
                        "source_url": p.source_url,
                        "official_status": p.official_status,
                    }
                    for p in q.provenance_records
                ]
            })

        return output
