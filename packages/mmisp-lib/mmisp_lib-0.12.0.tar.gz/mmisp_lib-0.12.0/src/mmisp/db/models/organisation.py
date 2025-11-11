import uuid
from datetime import datetime
from typing import Self

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin
from mmisp.db.types import DBUUID, DBListJson

from ..database import Base


class Organisation(Base, DictMixin["OrganisationDict"]):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    date_created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    date_modified: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description: Mapped[str | None] = mapped_column(Text, default="")
    type: Mapped[str] = mapped_column(String(255))
    nationality: Mapped[str] = mapped_column(String(255))
    sector: Mapped[str] = mapped_column(String(255))
    created_by: Mapped[int] = mapped_column(Integer, default=0)
    uuid: Mapped[str | None] = mapped_column(DBUUID, unique=True, default=uuid.uuid4)
    contacts: Mapped[str | None] = mapped_column(Text)
    local: Mapped[bool] = mapped_column(Boolean, default=False)
    restricted_to_domain: Mapped[list[str] | None] = mapped_column(DBListJson, default=list)
    landingpage: Mapped[str | None] = mapped_column(Text)
    __table_args__ = ({"extend_existing": True},)

    # Relationship to users
    users = relationship("User", back_populates="org", lazy="raise_on_sql")
    creator = relationship(
        "User", primaryjoin="Organisation.created_by == User.id", foreign_keys=created_by, lazy="selectin"
    )
    events = relationship(
        "Event", primaryjoin="Organisation.id == Event.org_id", back_populates="org", lazy="raise_on_sql"
    )  # type:ignore[assignment,var-annotated]
    events_created = relationship(
        "Event", primaryjoin="Organisation.id == Event.orgc_id", back_populates="orgc", lazy="raise_on_sql"
    )  # type:ignore[assignment,var-annotated]

    galaxy_clusters = relationship(
        "GalaxyCluster",
        primaryjoin="Organisation.id == GalaxyCluster.org_id",
        back_populates="org",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.org_id",
    )  # type:ignore[assignment,var-annotated]
    galaxy_clusters_created = relationship(
        "GalaxyCluster",
        primaryjoin="Organisation.id == GalaxyCluster.orgc_id",
        back_populates="orgc",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.orgc_id",
    )  # type:ignore[assignment,var-annotated]

    _sharing_group_orgs = relationship(
        "SharingGroupOrg",
        primaryjoin="Organisation.id == SharingGroupOrg.org_id",
        foreign_keys="SharingGroupOrg.org_id",
        viewonly=True,
        lazy="selectin",
    )

    @property
    def _sharing_group_ids(self: Self) -> list[int]:
        return [x.sharing_group_id for x in self._sharing_group_orgs]


#
