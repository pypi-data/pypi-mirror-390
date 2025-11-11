import warnings

from .types import DBUUID

warnings.warn("DBUUID is now part of mmisp.db.types", DeprecationWarning, stacklevel=2)

__all__ = ["DBUUID"]
