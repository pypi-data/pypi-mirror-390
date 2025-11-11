from time import time

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin

from ..database import Base
from .organisation import Organisation


class User(Base, UpdateMixin, DictMixin["UserDict"]):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(Organisation.id), index=True)
    server_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    autoalert: Mapped[bool] = mapped_column(Boolean, default=False)
    authkey: Mapped[str | None] = mapped_column(String(40), default=None)
    invited_by: Mapped[int] = mapped_column(Integer, default=0)
    gpgkey: Mapped[str | None] = mapped_column(Text)
    certif_public: Mapped[str | None] = mapped_column(Text)
    nids_sid: Mapped[int] = mapped_column(Integer, default=0)
    termsaccepted: Mapped[bool] = mapped_column(Boolean, default=False)
    newsread: Mapped[int | None] = mapped_column(Integer, default=0)
    role_id: Mapped[int] = mapped_column(Integer, default=6)
    change_pw: Mapped[int] = mapped_column(Integer, default=0)
    contactalert: Mapped[bool] = mapped_column(Boolean, default=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    expiration: Mapped[bool | None] = mapped_column(DateTime, default=None)
    current_login: Mapped[int | None] = mapped_column(Integer, default=0)
    last_login: Mapped[int | None] = mapped_column(Integer, default=0)
    force_logout: Mapped[bool] = mapped_column(Boolean, default=False)
    date_created: Mapped[int | None] = mapped_column(Integer, default=time)
    date_modified: Mapped[int | None] = mapped_column(Integer, default=time, onupdate=time)
    sub: Mapped[str | None] = mapped_column(String(255), unique=True)
    external_auth_required: Mapped[bool] = mapped_column(Boolean, default=False)
    external_auth_key: Mapped[str | None] = mapped_column(Text)
    last_api_access: Mapped[int | None] = mapped_column(Integer, default=0)
    notification_daily: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_weekly: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_monthly: Mapped[bool] = mapped_column(Boolean, default=False)
    totp: Mapped[str | None] = mapped_column(String(255))
    hotp_counter: Mapped[int | None] = mapped_column(Integer)
    last_pw_change: Mapped[int | None] = mapped_column(BigInteger)
    __table_args__ = ({"extend_existing": True},)

    # Relationships
    org = relationship("Organisation", back_populates="users", lazy="raise_on_sql")
    server = relationship(
        "Server",
        primaryjoin="Server.id == User.server_id",
        foreign_keys="User.server_id",
        back_populates="users",
        lazy="raise_on_sql",
    )
    role = relationship(
        "Role",
        primaryjoin="User.role_id == Role.id",
        foreign_keys="User.role_id",
        lazy="raise_on_sql",
    )
