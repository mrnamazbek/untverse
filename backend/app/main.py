from contextlib import asynccontextmanager
import time
import uuid
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import async_engine, AsyncSessionLocal
from app.db.init_db import init_db_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not exist and seed initial educational data
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        await init_db_data(session)

    yield
    # Shutdown
    await async_engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade SaaS платформа подготовки к ЕНТ по Информатике",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_strict_content_type(request: Request, call_next):
    """
    Strict Content-Type enforcement for mutating requests (POST, PUT, PATCH).
    Protects against malformed payloads and improves API correctness.
    """
    if request.method in {"POST", "PUT", "PATCH"}:
        content_length = request.headers.get("content-length")
        # Check if request has a payload body
        if content_length and int(content_length) > 0:
            content_type = request.headers.get("content-type", "").lower()
            allowed_types = (
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "application/x-ndjson",
            )
            if not any(content_type.startswith(t) for t in allowed_types):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "detail": f"Unsupported Media Type: '{content_type}'. Expected application/json, application/x-www-form-urlencoded, multipart/form-data, or application/x-ndjson."
                    },
                )
    return await call_next(request)


@app.middleware("http")
async def add_process_time_and_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", tags=["Оркестрация и Здоровье"])
async def health_check():
    """Liveness probe"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


@app.get("/ready", tags=["Оркестрация и Здоровье"])
async def readiness_check():
    """Readiness probe checking database connectivity"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )


app.include_router(api_router, prefix=settings.API_V1_STR)
