#!/usr/bin/env python3
"""
UNTverse Daily NTC news ingestion command.

The production scheduler invokes the authenticated API endpoint. This command is
kept for an operator who runs it *inside the deployed service* with its real
DATABASE_URL; it never creates or targets an ephemeral SQLite database.
"""
import sys
import os
import asyncio

# Add parent path to allow direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.core.config import settings
from app.services.ntc_news_ingestion import run_daily_ntc_news_ingestion


async def run_scheduled_ingestion():
    if settings.ENVIRONMENT == "production" and settings.DATABASE_URL.startswith("sqlite"):
        raise RuntimeError("Production ingestion requires a PostgreSQL DATABASE_URL")
    return await run_daily_ntc_news_ingestion()


if __name__ == "__main__":
    from typing import Dict, Any
    results = asyncio.run(run_scheduled_ingestion())
    print(f"INGESTION_SUMMARY: {results}")
