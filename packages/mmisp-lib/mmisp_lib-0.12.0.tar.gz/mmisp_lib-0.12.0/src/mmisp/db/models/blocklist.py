from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mmisp.db.types import DBUUID

from ..database import Base


class GalaxyClusterBlocklist(Base):
    __tablename__ = "galaxy_cluster_blocklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cluster_uuid: Mapped[str] = mapped_column(String(40), unique=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    cluster_info: Mapped[str] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
    cluster_orgc: Mapped[int] = mapped_column(String(255))
    __table_args__ = ({"extend_existing": True},)


class EventBlocklist(Base):
    __tablename__ = "event_blocklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_uuid: Mapped[str] = mapped_column(DBUUID, unique=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    event_info: Mapped[str] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
    event_orgc: Mapped[int] = mapped_column(String(255))
    __table_args__ = ({"extend_existing": True},)


class OrgBlocklist(Base):
    __tablename__ = "org_blocklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_uuid: Mapped[str] = mapped_column(DBUUID, unique=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    org_name: Mapped[str] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(Text)
    __table_args__ = ({"extend_existing": True},)
