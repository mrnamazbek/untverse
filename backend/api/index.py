"""Vercel's FastAPI entry point.

The import path is deliberately tiny: the application lives in ``app.main``
and Vercel discovers this module as the single ASGI function for the backend
project whose root directory is ``backend``.
"""

from app.main import app

__all__ = ["app"]
