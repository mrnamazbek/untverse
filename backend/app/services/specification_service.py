from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.specification import (
    ExamType, Subject, ExamSpecification, SpecificationSection, SpecificationTopic,
    CurrentUntRule, SpecificationStatus
)


class SpecificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_current_unt_rules(self, exam_year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Returns structured official facts about the current UNT exam season.
        """
        query = select(CurrentUntRule).where(CurrentUntRule.is_active == True)
        if exam_year:
            query = query.where(CurrentUntRule.exam_year == exam_year)
        else:
            query = query.order_by(CurrentUntRule.exam_year.desc())

        result = await self.session.execute(query)
        rule = result.scalars().first()
        if not rule:
            return None

        return {
            "exam_year": rule.exam_year,
            "is_active": rule.is_active,
            "structure": {
                "total_questions": rule.total_questions,
                "maximum_score": rule.maximum_score,
                "duration_minutes": rule.duration_minutes,
                "duration_formatted": f"{rule.duration_minutes // 60} сағат {rule.duration_minutes % 60} минут (240 мин)",
                "passing_threshold_total": rule.passing_threshold_total,
                "passing_threshold_per_subject": rule.passing_threshold_per_subject,
            },
            "informatics_specifics": {
                "questions_count": rule.informatics_questions_count,
                "max_score": rule.informatics_max_score,
                "format": "Бір дұрыс жауапты (35), бір немесе бірнеше дұрыс жауапты (10), мәтінмәндік тапсырмалар (5)",
            },
            "subjects_breakdown": rule.subjects_structure,
            "profile_combinations": rule.profile_combinations,
            "testing_periods": rule.testing_periods,
            "important_deadlines": rule.important_deadlines,
            "grant_rules_summary": rule.grant_rules_summary,
            "official_source_urls": rule.official_source_urls,
            "last_verified_at": rule.last_verified_at.isoformat() if rule.last_verified_at else None,
            "verified_by": rule.verified_by,
        }

    async def get_informatics_specifications(self, locale: str = "kk", year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves versioned Informatics exam specifications with full hierarchical taxonomy.
        """
        query = (
            select(ExamSpecification)
            .options(
                selectinload(ExamSpecification.sections)
                .selectinload(SpecificationSection.topics)
            )
            .join(Subject)
            .where(Subject.code == "informatics")
        )
        if year:
            query = query.where(ExamSpecification.exam_year == year)
        else:
            query = query.order_by(ExamSpecification.exam_year.desc())

        result = await self.session.execute(query)
        specs = result.scalars().all()

        output = []
        for spec in specs:
            # Pick localized titles
            title = spec.title_kk if locale == "kk" else (spec.title_ru if locale == "ru" else spec.title_en)
            
            sections_data = []
            for sec in spec.sections:
                sec_title = sec.title_kk if locale == "kk" else (sec.title_ru if locale == "ru" else sec.title_en)
                
                topics_data = []
                for top in sec.topics:
                    top_title = top.title_kk if locale == "kk" else (top.title_ru if locale == "ru" else top.title_en)
                    topics_data.append({
                        "id": top.id,
                        "code": top.code,
                        "title": top_title,
                        "learning_objectives": top.learning_objectives,
                        "order_index": top.order_index,
                    })

                sections_data.append({
                    "id": sec.id,
                    "code": sec.code,
                    "title": sec_title,
                    "description": sec.description,
                    "weight_percentage": sec.weight_percentage,
                    "question_count_est": sec.question_count_est,
                    "order_index": sec.order_index,
                    "topics": topics_data,
                })

            output.append({
                "id": spec.id,
                "exam_year": spec.exam_year,
                "version": spec.version,
                "title": title,
                "status": spec.status,
                "valid_from": spec.valid_from.isoformat() if spec.valid_from else None,
                "valid_to": spec.valid_to.isoformat() if spec.valid_to else None,
                "total_questions": spec.total_questions,
                "max_score": spec.max_score,
                "source_url": spec.source_url,
                "content_hash": spec.content_hash,
                "sections": sections_data,
            })

        return output
