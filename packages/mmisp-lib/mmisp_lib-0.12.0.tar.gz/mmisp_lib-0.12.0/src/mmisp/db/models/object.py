from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.database import Base
from mmisp.db.mixins import DictMixin
from mmisp.db.types import DBUUID, DateTimeEpoch, DBListJson, DBObjectJson
from mmisp.lib.uuid import uuid


class Object(Base, DictMixin["ObjectDict"]):
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str | None] = mapped_column(DBUUID, unique=True, default=uuid)
    name: Mapped[str | None] = mapped_column(String(255), index=True)
    meta_category: Mapped[str | None] = mapped_column("meta-category", String(255), index=True)
    description: Mapped[str | None] = mapped_column(String(255))
    # Comment for template_uuid: in MISP it is called object_template_uuid
    template_uuid: Mapped[str | None] = mapped_column(String(255), index=True, default=None)
    template_version: Mapped[int] = mapped_column(Integer, index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTimeEpoch, index=True, default=0)
    distribution: Mapped[int] = mapped_column(Integer, index=True, default=0)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sharing_groups.id"), index=True)
    comment: Mapped[str] = mapped_column(String(255))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    first_seen: Mapped[int | None] = mapped_column(Integer, index=True, default=None)
    last_seen: Mapped[int | None] = mapped_column(Integer, index=True, default=None)
    __table_args__ = ({"extend_existing": True},)

    attributes = relationship(
        "Attribute",
        primaryjoin="Object.id == Attribute.object_id",
        back_populates="mispobject",
        lazy="raise_on_sql",
        foreign_keys="Attribute.object_id",
    )  # type:ignore[var-annotated]
    event = relationship(
        "Event",
        back_populates="mispobjects",
        lazy="raise_on_sql",
    )  # type:ignore[var-annotated]


class ObjectTemplate(Base, DictMixin["ObjectTemplateDict"]):
    __tablename__ = "object_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    org_id: Mapped[int] = mapped_column(Integer, index=True)
    uuid: Mapped[str | None] = mapped_column(DBUUID, unique=True, default=uuid, index=True)
    name: Mapped[Optional[str] | None] = mapped_column(String(255), index=True)
    meta_category: Mapped[Optional[str] | None] = mapped_column(
        "meta-category", String(255), index=True, key="meta_category"
    )
    description: Mapped[Optional[str] | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer)
    requirements: Mapped[dict | None] = mapped_column(DBObjectJson)
    fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = ({"extend_existing": True},)

    elements: Mapped[list["ObjectTemplateElement"]] = relationship(
        "ObjectTemplateElement", back_populates="object_template", lazy="raise_on_sql"
    )


class ObjectTemplateElement(Base, DictMixin["ObjectTemplateElementDict"]):
    __tablename__ = "object_template_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    object_template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ObjectTemplate.id, ondelete="CASCADE"), index=True
    )
    object_relation: Mapped[Optional[str] | None] = mapped_column(String(255), index=True)
    type: Mapped[Optional[str] | None] = mapped_column(Text, index=True)
    ui_priority: Mapped[int] = mapped_column("ui-priority", Integer, key="ui_priority")
    categories: Mapped[list[str] | None] = mapped_column(DBListJson)
    sane_default: Mapped[list[str] | None] = mapped_column(DBListJson)
    values_list: Mapped[list[str] | None] = mapped_column(DBListJson)
    description: Mapped[Optional[str] | None] = mapped_column(Text)
    disable_correlation: Mapped[Optional[bool] | None] = mapped_column(Boolean)
    multiple: Mapped[bool] = mapped_column(Boolean, default=False)

    object_template: Mapped[ObjectTemplate] = relationship(
        ObjectTemplate, back_populates="elements", lazy="raise_on_sql"
    )
