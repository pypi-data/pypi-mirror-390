from sqlalchemy import BigInteger, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.db.mypy import Mapped, mapped_column
from mmisp.lib.uuid import uuid

from ..mixins import DictMixin
from .attribute import Attribute
from .event import Event
from .organisation import Organisation


class Sighting(Base, DictMixin):
    __tablename__ = "sightings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str | None] = mapped_column(String(40), unique=True, default=uuid)
    attribute_id: Mapped[int] = mapped_column(Integer, ForeignKey(Attribute.id), index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey(Event.id), index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(Organisation.id), index=True)
    date_sighting: Mapped[int] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(255), index=True, default="")
    type: Mapped[int | None] = mapped_column(Integer, index=True, default=0)
    __table_args__ = ({"extend_existing": True},)
