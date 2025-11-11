from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text

from mmisp.db.database import Base
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.db.mypy import Mapped, mapped_column
from mmisp.lib.uuid import uuid


class ShadowAttribute(Base):
    __tablename__ = "shadow_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    old_id: Mapped[int | None] = mapped_column(Integer, default=0)
    uuid: Mapped[str] = mapped_column(String(40), unique=True, default=uuid, index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(Organisation.id), index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey(Event.id), index=True)
    event_uuid: Mapped[str] = mapped_column(String(40), ForeignKey(Event.uuid), index=True)
    event_org_id: Mapped[int] = mapped_column(Integer, ForeignKey(Organisation.id))
    type: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    value1: Mapped[str | None] = mapped_column(Text)
    value2: Mapped[str | None] = mapped_column(Text)
    to_ids: Mapped[bool] = mapped_column(Boolean, default=True)
    comment: Mapped[str] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    proposal_to_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    disable_correlation: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[int] = mapped_column(Integer, default=0)
    first_seen: Mapped[int | None] = mapped_column(BigInteger)
    last_seen: Mapped[str | None] = mapped_column(BigInteger)
    __table_args__ = ({"extend_existing": True},)
