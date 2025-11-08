"""
Top-level package for the context-control toolkit.
Exports the core client and creates a FastAPI app for convenience.
"""

from .api import create_app  # noqa: F401
from .client import ContextControlClient  # noqa: F401

app = create_app()

__all__ = ["ContextControlClient", "app", "create_app"]

