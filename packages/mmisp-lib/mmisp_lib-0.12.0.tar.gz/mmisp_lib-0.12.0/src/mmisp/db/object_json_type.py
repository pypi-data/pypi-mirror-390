import warnings

from .types import DBObjectJson

warnings.warn("DBObjectJson is now part of mmisp.db.types", DeprecationWarning, stacklevel=2)

__all__ = ["DBObjectJson"]
