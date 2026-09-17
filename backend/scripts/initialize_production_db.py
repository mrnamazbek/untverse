"""One-time, operator-invoked production database bootstrap.

Run this only against a new database after ``alembic upgrade head``. It covers
the legacy data-platform tables which predate their Alembic migration, then
seeds the idempotent reference data. It is never imported by the Vercel
Function, so cold starts cannot issue DDL or seed writes.
"""

from __future__ import annotations

import asyncio

from app.db.base import Base
from app.db.init_db import init_db_data
from app.db.session import AsyncSessionLocal, async_engine
import app.models  # noqa: F401 - register every SQLAlchemy model with Base


async def main() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await init_db_data(session)

    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
