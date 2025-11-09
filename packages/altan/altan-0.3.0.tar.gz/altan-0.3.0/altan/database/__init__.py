"""
Altan SDK - Database Module (DEPRECATED)

⚠️  DEPRECATION NOTICE ⚠️
This database module is deprecated and will be removed in a future version.
Please migrate to alternative database solutions.

PostgREST-style database operations with chainable query interface.
"""

import warnings
from .database import Database, QueryBuilder

# Issue deprecation warning when module is imported
warnings.warn(
    "The altan.database module is deprecated and will be removed in a future version. "
    "Please migrate to alternative database solutions.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["Database", "QueryBuilder"]
