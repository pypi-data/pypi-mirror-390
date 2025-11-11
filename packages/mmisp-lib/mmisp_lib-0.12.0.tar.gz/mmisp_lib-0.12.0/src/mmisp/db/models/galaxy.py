from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.mypy import Mapped, mapped_column
from mmisp.db.types import DBUUID
from mmisp.lib.uuid import uuid

from ..database import Base


class Galaxy(Base, DictMixin["GalaxyDict"], UpdateMixin):
    __tablename__ = "galaxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(DBUUID, unique=True, default=uuid)
    name: Mapped[str] = mapped_column(String(255), default="", index=True)
    type: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(255))
    icon: Mapped[str] = mapped_column(String(255), default="")
    namespace: Mapped[str] = mapped_column(String(255), default="misp", index=True)
    kill_chain_order: Mapped[str | None] = mapped_column(Text)
    """must be serialized"""
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    local_only: Mapped[bool] = mapped_column(Boolean, default=False)
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    org_id: Mapped[int] = mapped_column(Integer)
    orgc_id: Mapped[int] = mapped_column(Integer)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    modified: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    distribution: Mapped[int] = mapped_column(Integer)
    __table_args__ = ({"extend_existing": True},)

    galaxy_clusters = relationship(
        "GalaxyCluster",
        back_populates="galaxy",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]
