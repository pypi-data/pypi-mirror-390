import logging
from functools import cached_property
from typing import Self
from uuid import uuid4 as _uuid4

from sqlalchemy import Boolean, Integer, String

from mmisp.db.mixins import UpdateMixin
from mmisp.db.mypy import Mapped, mapped_column

from ...workflows.graph import WorkflowGraph
from ...workflows.legacy import JSONGraphType
from ..database import Base
from .log import Log


def uuid() -> str:
    return str(_uuid4())


class Workflow(Base, UpdateMixin):
    """
    A python class representation of the database model for workflows in MISP.

    The most central of the attributes in this model is the data attribute,
    containing the information about the workflow structure and the modules contained in the workflow,
    represented/stored as a JSON-String.
    (The other attributes are what their name sais, e.g. counter represents the numer
    of times the workflow was executed.)
    """

    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(40), default=uuid, index=True)
    name: Mapped[str] = mapped_column(String(191), index=True)
    description: Mapped[str] = mapped_column(String(191))
    timestamp: Mapped[int] = mapped_column(Integer, default=0, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    counter: Mapped[int] = mapped_column(Integer, default=0)
    trigger_id: Mapped[str] = mapped_column(String(191), index=True)
    debug_enabled: Mapped[bool] = mapped_column(Boolean, default=0)
    data: Mapped[WorkflowGraph | None] = mapped_column(JSONGraphType, default=0)
    __table_args__ = ({"extend_existing": True},)

    def __init__(self: Self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @cached_property
    def _logger(self: Self) -> logging.LoggerAdapter:
        _logger = logging.LoggerAdapter(
            logging.getLogger(f"mmisp.workflows.{self.name}"),
            extra=dict(
                dbmodel=Log,
                model="Workflow",
                model_id=self.id,
                action="execute_workflow",
                user_id=0,
                email="SYSTEM",
                org="SYSTEM",
                description="",
                change="",
                ip="",
            ),
        )
        if self.debug_enabled:
            _logger.setLevel(logging.DEBUG)
        return _logger

    def get_logger(self: Self) -> logging.LoggerAdapter:
        return self._logger
