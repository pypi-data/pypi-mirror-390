from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.types import DBUUID
from mmisp.lib.uuid import uuid

from ..database import Base


class SharingGroup(Base, UpdateMixin, DictMixin["SharingGroupDict"]):
    __tablename__ = "sharing_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    releasability: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    uuid: Mapped[str] = mapped_column(DBUUID, unique=True, default=uuid)
    organisation_uuid: Mapped[str] = mapped_column(DBUUID)
    org_id: Mapped[int] = mapped_column(Integer, index=True)  # the organisation that created the sharing group
    sync_user_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    local: Mapped[bool] = mapped_column(Boolean, default=True)
    roaming: Mapped[bool] = mapped_column(Boolean, default=False)

    creator_org = relationship(
        "Organisation",
        primaryjoin="SharingGroup.org_id == Organisation.id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroup.org_id",
    )  # type:ignore[assignment,var-annotated]
    organisations = relationship(
        "Organisation",
        primaryjoin="SharingGroup.id == SharingGroupOrg.sharing_group_id",
        secondary="sharing_group_orgs",
        secondaryjoin="SharingGroupOrg.org_id == Organisation.id",
        lazy="selectin",
        viewonly=True,
    )

    sharing_group_orgs = relationship(
        "SharingGroupOrg",
        primaryjoin="SharingGroup.id == SharingGroupOrg.sharing_group_id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupOrg.sharing_group_id",
    )  # type:ignore[assignment,var-annotated]
    sharing_group_servers = relationship(
        "SharingGroupServer",
        primaryjoin="SharingGroup.id == SharingGroupServer.sharing_group_id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupServer.sharing_group_id",
    )  # type:ignore[assignment,var-annotated]


class SharingGroupOrg(Base, UpdateMixin, DictMixin["SharingGroupOrgDict"]):
    __tablename__ = "sharing_group_orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sharing_group_id: Mapped[int] = mapped_column(Integer, index=True)
    org_id: Mapped[int] = mapped_column(Integer, index=True)
    extend: Mapped[bool] = mapped_column(Boolean, default=False)

    organisation = relationship(
        "Organisation",
        primaryjoin="SharingGroupOrg.org_id == Organisation.id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupOrg.org_id",
    )  # type:ignore[assignment,var-annotated]


class SharingGroupServer(Base, UpdateMixin, DictMixin["SharingGroupServerDict"]):
    __tablename__ = "sharing_group_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sharing_group_id: Mapped[int] = mapped_column(Integer, index=True)
    server_id: Mapped[int] = mapped_column(Integer, index=True)
    all_orgs: Mapped[bool] = mapped_column(Boolean, index=True, default=False)

    server = relationship(
        "Server",
        primaryjoin="SharingGroupServer.server_id == Server.id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupServer.server_id",
    )  # type:ignore[assignment,var-annotated]
