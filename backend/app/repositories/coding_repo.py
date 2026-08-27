from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.coding import CodingTask, TestCase, CodingSubmission
from app.repositories.base import BaseRepository


class CodingRepository(BaseRepository[CodingTask]):
    def __init__(self, session: AsyncSession):
        super().__init__(CodingTask, session)

    async def get_by_id_with_tests(self, task_id: int, include_hidden: bool = True) -> Optional[CodingTask]:
        result = await self.session.execute(
            select(CodingTask)
            .options(selectinload(CodingTask.test_cases))
            .where(CodingTask.id == task_id)
        )
        return result.scalars().first()

    async def get_by_slug_with_tests(self, slug: str) -> Optional[CodingTask]:
        result = await self.session.execute(
            select(CodingTask)
            .options(selectinload(CodingTask.test_cases))
            .where(CodingTask.slug == slug)
        )
        return result.scalars().first()

    async def list_all_active(self, difficulty: Optional[str] = None) -> List[CodingTask]:
        query = select(CodingTask).where(CodingTask.is_published == True)
        if difficulty:
            query = query.where(CodingTask.difficulty == difficulty)
        result = await self.session.execute(query.order_by(CodingTask.id))
        return list(result.scalars().all())

    async def save_submission(
        self,
        user_id: int,
        task_id: int,
        source_code: str,
        status: str,
        passed_tests: int,
        total_tests: int,
        execution_time_ms: float,
        error_output: Optional[str] = None,
    ) -> CodingSubmission:
        submission = CodingSubmission(
            user_id=user_id,
            task_id=task_id,
            source_code=source_code,
            status=status,
            passed_tests=passed_tests,
            total_tests=total_tests,
            execution_time_ms=execution_time_ms,
            error_output=error_output,
            submitted_at=datetime.now(timezone.utc),
        )
        self.session.add(submission)
        await self.session.flush()
        return submission

    async def get_user_solved_task_ids(self, user_id: int) -> List[int]:
        result = await self.session.execute(
            select(CodingSubmission.task_id)
            .where(CodingSubmission.user_id == user_id, CodingSubmission.status == "accepted")
            .distinct()
        )
        return list(result.scalars().all())
