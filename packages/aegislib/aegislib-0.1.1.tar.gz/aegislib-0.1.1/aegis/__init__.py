"""Aegis Python SDK - Secure AI tool guard integration.

This SDK provides a simple decorator to integrate
policy-based AI tool security into your agent workflows.
"""

from ._version import __version__

# Core API
from .config import AegisConfig
from .decision import DecisionClient
from .errors import (
    AegisError,
    AuthError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
)
from .guard import aegis_guard

__all__ = [
    "__version__",
    # Core components
    "AegisConfig",
    "DecisionClient",
    "aegis_guard",
    # Error types
    "AegisError",
    "AuthError",
    "ForbiddenError",
    "BadRequestError",
    "NotFoundError",
]
