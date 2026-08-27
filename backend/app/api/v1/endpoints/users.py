from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserProfileResponse, UserProfileUpdate
from app.schemas.auth import FullUserResponse
from app.repositories.user_repo import UserRepository

router = APIRouter()


@router.get("/me", response_model=FullUserResponse, summary="Получить текущего пользователя")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user.profile


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    updated = await user_repo.update_profile(
        user_id=current_user.id,
        display_name=update_in.display_name,
        avatar_url=update_in.avatar_url,
        bio=update_in.bio,
        target_unt_score=update_in.target_unt_score
    )
    await db.commit()
    return updated
