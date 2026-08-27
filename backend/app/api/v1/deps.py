from typing import AsyncGenerator, Optional, List
from fastapi import Depends, HTTPException, status, Header, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.repositories.user_repo import UserRepository
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    access_token_cookie: Optional[str] = Cookie(default=None, alias="access_token")
) -> User:
    token = bearer_token or access_token_cookie
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не предоставлен токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен доступа",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные токена")

    user_repo = UserRepository(db)
    user = await user_repo.get_with_profile(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь заблокирован")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения данной операции"
            )
        return current_user
    return role_checker


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    access_token_cookie: Optional[str] = Cookie(default=None, alias="access_token")
) -> Optional[User]:
    token = bearer_token or access_token_cookie
    if not token:
        return None
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user_repo = UserRepository(db)
    return await user_repo.get_with_profile(int(user_id))


require_admin = require_roles(["admin"])
require_teacher_or_admin = require_roles(["teacher", "admin"])
