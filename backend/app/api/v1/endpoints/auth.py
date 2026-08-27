from fastapi import APIRouter, Depends, Response, status, Cookie
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, TokenResponse, TokenRefreshRequest, UserResponse
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    token_resp = await service.register(user_in)
    await db.commit()

    # Set secure HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        max_age=60 * 60 * 24
    )
    response.set_cookie(
        key="refresh_token",
        value=token_resp.refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30
    )
    return token_resp


@router.post("/login", response_model=TokenResponse)
async def login(
    login_in: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    token_resp = await service.login(login_in)
    await db.commit()

    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24
    )
    response.set_cookie(
        key="refresh_token",
        value=token_resp.refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30
    )
    return token_resp


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    request: Optional[TokenRefreshRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db)
):
    token_str = None
    if request and request.refresh_token:
        token_str = request.refresh_token
    elif refresh_token_cookie:
        token_str = refresh_token_cookie

    if not token_str:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException(detail="Refresh токен не передан")

    service = AuthService(db)
    token_resp = await service.refresh_tokens(token_str)
    await db.commit()

    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24
    )
    response.set_cookie(
        key="refresh_token",
        value=token_resp.refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30
    )
    return token_resp


@router.post("/logout")
async def logout(
    response: Response,
    request: Optional[TokenRefreshRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db)
):
    token_str = request.refresh_token if request else refresh_token_cookie
    if token_str:
        service = AuthService(db)
        await service.logout(token_str)
        await db.commit()

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Успешный выход из системы"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
