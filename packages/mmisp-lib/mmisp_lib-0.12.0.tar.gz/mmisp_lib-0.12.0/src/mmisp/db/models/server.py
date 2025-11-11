from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import relationship

from mmisp.db.mixins import DictMixin
from mmisp.db.mypy import Mapped, mapped_column

from ..database import Base


class Server(Base, DictMixin["ServerDict"]):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255))
    authkey: Mapped[str] = mapped_column(String(40))
    org_id: Mapped[int] = mapped_column(Integer, index=True)
    push: Mapped[bool] = mapped_column(Boolean)
    pull: Mapped[bool] = mapped_column(Boolean)
    push_sightings: Mapped[bool] = mapped_column(Boolean, default=False)
    push_galaxy_clusters: Mapped[bool] = mapped_column(Boolean, default=False)
    pull_galaxy_clusters: Mapped[bool] = mapped_column(Boolean, default=False)
    push_analyst_data: Mapped[bool] = mapped_column(Boolean, default=False)
    pull_analyst_data: Mapped[bool] = mapped_column(Boolean, default=False)
    last_pulled_id: Mapped[int | None] = mapped_column("lastpulledid", Integer)
    last_pushed_id: Mapped[int | None] = mapped_column("lastpushedid", Integer)
    organization: Mapped[str | None] = mapped_column(String(10), default=None)
    remote_org_id: Mapped[int] = mapped_column(Integer, index=True)
    publish_without_email: Mapped[bool] = mapped_column(Boolean, default=False)
    unpublish_event: Mapped[bool] = mapped_column(Boolean, default=False)
    self_signed: Mapped[bool] = mapped_column(Boolean)
    pull_rules: Mapped[str] = mapped_column(Text)
    push_rules: Mapped[str] = mapped_column(Text)
    cert_file: Mapped[str | None] = mapped_column(String(255))
    client_cert_file: Mapped[str | None] = mapped_column(String(255))
    internal: Mapped[bool] = mapped_column(Boolean, default=False)
    skip_proxy: Mapped[bool] = mapped_column(Boolean, default=False)
    caching_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, index=True)
    remove_missing_tags: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = ({"extend_existing": True},)

    organisation = relationship(
        "Organisation",
        primaryjoin="Server.org_id == Organisation.id",
        lazy="raise_on_sql",
        foreign_keys="Server.org_id",
    )  # type:ignore[assignment,var-annotated]
    remote_organisation = relationship(
        "Organisation",
        primaryjoin="Server.remote_org_id == Organisation.id",
        lazy="raise_on_sql",
        foreign_keys="Server.remote_org_id",
    )  # type:ignore[assignment,var-annotated]
    users = relationship(
        "User",
        primaryjoin="Server.id == User.server_id",
        foreign_keys="User.server_id",
        back_populates="server",
        lazy="raise_on_sql",
    )
