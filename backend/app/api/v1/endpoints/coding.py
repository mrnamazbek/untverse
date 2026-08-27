from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user, get_optional_current_user
from app.models.user import User
from app.repositories.coding_repo import CodingRepository
from app.services.code_execution_service import CodeExecutionService
from app.services.gamification_service import GamificationService
from app.schemas.coding import (
    CodingTaskListItem, CodingTaskResponse, CodeRunRequest, CodeRunResponse, TestCaseResponse
)
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=List[CodingTaskListItem])
@router.get("/tasks", response_model=List[CodingTaskListItem])
async def list_coding_tasks(
    difficulty: Optional[str] = None,
    topic_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodingRepository(db)
    tasks = await repo.list_all_active(difficulty)
    solved_ids = set()
    if current_user:
        solved_ids = set(await repo.get_user_solved_task_ids(current_user.id))

    return [
        CodingTaskListItem(
            id=t.id,
            topic_id=t.topic_id,
            title=t.title,
            slug=t.slug,
            difficulty=t.difficulty,
            xp_reward=t.xp_reward,
            is_solved_by_user=(t.id in solved_ids)
        ) for t in tasks
    ]


@router.get("/{task_id}", response_model=CodingTaskResponse)
@router.get("/tasks/{task_id}", response_model=CodingTaskResponse)
async def get_coding_task(
    task_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodingRepository(db)
    task = await repo.get_by_id_with_tests(task_id)
    if not task or not task.is_published:
        raise NotFoundException(detail="Задача не найдена")

    is_solved = False
    if current_user:
        solved_ids = await repo.get_user_solved_task_ids(current_user.id)
        is_solved = task.id in solved_ids

    # Exclude hidden test cases for student view
    visible_tests = [tc for tc in task.test_cases if not tc.is_hidden]

    return CodingTaskResponse(
        id=task.id,
        topic_id=task.topic_id,
        title=task.title,
        slug=task.slug,
        description=task.description,
        starter_code=task.starter_code,
        difficulty=task.difficulty,
        time_limit_seconds=task.time_limit_seconds,
        memory_limit_mb=task.memory_limit_mb,
        xp_reward=task.xp_reward,
        is_published=task.is_published,
        test_cases=[TestCaseResponse.model_validate(tc) for tc in visible_tests],
        is_solved_by_user=is_solved
    )


@router.post("/{task_id}/run", response_model=CodeRunResponse)
@router.post("/tasks/{task_id}/run", response_model=CodeRunResponse)
async def run_coding_task(
    task_id: int,
    request: CodeRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodingRepository(db)
    task = await repo.get_by_id_with_tests(task_id)
    if not task:
        raise NotFoundException(detail=f"Задача ID {task_id} не найдена")

    raw_test_cases = [
        {
            "id": tc.id,
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            "is_hidden": tc.is_hidden
        } for tc in task.test_cases
    ]

    exec_result = await CodeExecutionService.execute_task(
        source_code=request.source_code,
        test_cases=raw_test_cases,
        time_limit_seconds=task.time_limit_seconds
    )

    # Check previous solve state
    already_solved_ids = set(await repo.get_user_solved_task_ids(current_user.id))
    is_first_time_solve = (exec_result.status == "accepted" and task.id not in already_solved_ids)

    # Save submission
    await repo.save_submission(
        user_id=current_user.id,
        task_id=task.id,
        source_code=request.source_code,
        status=exec_result.status,
        passed_tests=exec_result.passed_tests,
        total_tests=exec_result.total_tests,
        execution_time_ms=exec_result.execution_time_ms,
        error_output=exec_result.error_output
    )

    # Gamification reward if passed
    if is_first_time_solve:
        gamification = GamificationService(db)
        new_total_xp, new_level, leveled_up = await gamification.handle_coding_task_completed(
            user_id=current_user.id,
            task_id=task.id,
            xp_reward=task.xp_reward
        )
        exec_result.xp_earned = task.xp_reward
        exec_result.new_total_xp = new_total_xp
        exec_result.new_level = new_level
        exec_result.leveled_up = leveled_up
    else:
        profile = (await repo.session.get(User, current_user.id)).profile
        if profile:
            exec_result.new_total_xp = profile.total_xp
            exec_result.new_level = profile.current_level

    await db.commit()
    return exec_result
