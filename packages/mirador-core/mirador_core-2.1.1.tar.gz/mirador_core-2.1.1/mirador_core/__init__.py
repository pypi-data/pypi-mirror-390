"""
Mirador Core Library
====================

A unified library for the Mirador AI ecosystem.

This package provides shared functionality across all Mirador tools:
- Error handling with circuit breakers and fallbacks (mirador_core.core)
- Context management and caching (mirador_core.context)
- Constraint validation for time/energy/financial allocations (mirador_core.constraints)

Version: 2.1.0
"""

__version__ = "2.1.0"
__author__ = "Matthew David Scott"

# Core components
from . import core
from . import context
from . import constraints

__all__ = [
    "core",
    "context",
    "constraints",
    "__version__",
    "__author__"
]
