import logging
import typing
from datetime import datetime
from typing import Self, Type

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import Comparator, hybrid_method, hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.types import DBUUID, DateTimeEpoch
from mmisp.lib.attributes import categories, default_category, mapper_safe_clsname_val, to_ids
from mmisp.lib.distribution import AttributeDistributionLevels
from mmisp.lib.permissions import Permission
from mmisp.lib.uuid import uuid

from ..database import AutoDictMeta, Base
from .event import Event
from .tag import Tag
from .user import User

if typing.TYPE_CHECKING:
    from sqlalchemy import ColumnExpressionArgument

    from .object import Object
else:
    ColumnExpressionArgument = typing.Any

logger = logging.getLogger("mmisp")


class AttributeComparator(Comparator):
    def __init__(self: Self, cls: typing.Any) -> None:
        self.cls = cls

    def __eq__(self: Self, other: typing.Any) -> ColumnExpressionArgument:
        # Overriding equality to check if the value matches either value1 or value1 + "|" + value2
        return or_(self.cls.value1 == other, self.cls.value1 + "|" + self.cls.value2 == other)


class Attribute(Base, UpdateMixin, DictMixin["AttributeDict"]):
    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(DBUUID, unique=True, default=uuid)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    object_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    object_relation: Mapped[str | None] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[str] = mapped_column(String(100), index=True)
    value1: Mapped[str] = mapped_column(Text)
    value2: Mapped[str] = mapped_column(Text, default="")
    to_ids: Mapped[bool] = mapped_column(Boolean, default=True)
    timestamp: Mapped[datetime] = mapped_column(DateTimeEpoch, default=0)
    distribution: Mapped[int] = mapped_column(Integer, default=0)
    sharing_group_id: Mapped[int] = mapped_column(Integer, index=True, default=0)
    comment: Mapped[str | None] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    disable_correlation: Mapped[bool] = mapped_column(Boolean, default=False)
    first_seen: Mapped[int | None] = mapped_column(BigInteger, index=True)
    last_seen: Mapped[int | None] = mapped_column(BigInteger, index=True)

    event: Mapped[Event] = relationship("Event", back_populates="attributes", lazy="selectin")
    mispobject: Mapped["Object"] = relationship(
        "Object",
        primaryjoin="Attribute.object_id == Object.id",
        back_populates="attributes",
        lazy="joined",
        foreign_keys="Attribute.object_id",
    )
    tags = relationship("Tag", secondary="attribute_tags", lazy="selectin", viewonly=True)
    attributetags = relationship(
        "AttributeTag",
        primaryjoin="Attribute.id == AttributeTag.attribute_id",
        back_populates="attribute",
        lazy="raise_on_sql",
        viewonly=True,
    )
    attributetags_galaxy = relationship(
        "AttributeTag",
        primaryjoin="and_(Attribute.id == AttributeTag.attribute_id, Tag.is_galaxy)",
        secondary="join(AttributeTag, Tag, AttributeTag.tag_id == Tag.id)",
        secondaryjoin="AttributeTag.tag_id == Tag.id",
        lazy="raise_on_sql",
        viewonly=True,
    )

    galaxy_tags = relationship(
        "Tag",
        secondary="attribute_tags",
        secondaryjoin="and_(AttributeTag.tag_id == Tag.id, Tag.is_galaxy)",
        lazy="raise_on_sql",
        overlaps="tags, events",
        viewonly=True,
    )
    local_tags = relationship(
        "Tag",
        secondary="attribute_tags",
        secondaryjoin="and_(AttributeTag.tag_id == Tag.id, AttributeTag.local)",
        lazy="raise_on_sql",
        viewonly=True,
    )
    nonlocal_tags = relationship(
        "Tag",
        secondary="attribute_tags",
        secondaryjoin="and_(AttributeTag.tag_id == Tag.id, not_(AttributeTag.local))",
        lazy="raise_on_sql",
        viewonly=True,
    )

    sharing_group = relationship(
        "SharingGroup",
        primaryjoin="Attribute.sharing_group_id == SharingGroup.id",
        lazy="raise_on_sql",
        foreign_keys="Attribute.sharing_group_id",
    )

    __mapper_args__ = {"polymorphic_on": "type"}

    def __init__(self: Self, *arg, **kwargs) -> None:
        if "value" in kwargs:
            split_val = kwargs["value"].split("|", 1)
            kwargs["value1"] = split_val[0]
            if len(split_val) == 2:
                kwargs["value2"] = split_val[1]

        super().__init__(*arg, **kwargs)

    async def add_tag(self: Self, db: AsyncSession, tag: "Tag", local: bool = False) -> "AttributeTag":
        if tag.local_only:
            local = True
        attribute_tag = AttributeTag(attribute=self, tag=tag, event_id=self.event_id, local=local)
        db.add(attribute_tag)
        await db.commit()
        await db.refresh(attribute_tag)
        return attribute_tag

    @hybrid_method
    def can_edit(self: Self, user: User) -> bool:
        """
        Checks if a user is allowed to modify an attribute based on
        whether he or someone of his organisation created the attribute.

        args:
            self: the attribute
            user: the user

        returns:
            true if the user has editing permission
        """
        if user is None:
            logger.debug("User is none")
            return False

        if user.role.check_permission(Permission.SITE_ADMIN):
            logger.debug("User is site admin")
            return True

        if user.role.check_permission(Permission.MODIFY_ORG):
            logger.debug("User has modify org permission")
            return self.event.orgc_id == user.org_id

        return False

    @can_edit.expression
    def can_edit(cls: Self, user: User) -> bool:
        """
        Checks if a user is allowed to modify an attribute based on
        whether he or someone of his organisation created the attribute.

        args:
            self: the attribute
            user: the user

        returns:
            true if the user has editing permission
        """
        condition = []
        condition.append(user is None)
        condition.append(user.role.check_permission(Permission.SITE_ADMIN))
        condition.append(
            and_(cls.event.has(Event.orgc_id == user.org_id), user.role.check_permission(Permission.MODIFY_ORG))
        )

        return or_(*condition)
        """
        return (
            user is None  # user is a worker
            or user.role.check_permission(Permission.SITE_ADMIN)
            or (user.org_id == cls.event.org_id and user.role.check_permission(Permission.MODIFY_ORG))
            or (user.org_id == cls.event.orgc_id)
        )
        """

    @hybrid_method
    def can_access(self: Self, user: User) -> bool:
        """
        Checks if a user is allowed to see and access an attribute based on
        whether the user  is part of the same group or organisation and/or creater organisation
        as well as the publishing status of the attribute with consideration of the event,
        the attribute is associated with.
        whether the attribute is part of the same group or organisation and or creating organisation and
        the publishing status of the attribute with
        consideration of the event the attribute is associated with.

         args:
            self: the attribute
            user: the user

        returns:
            true if the user has access permission
        """
        user_org_id = user.org_id

        if user is None or user.role.check_permission(Permission.SITE_ADMIN):
            return True  # User is a Worker or Site Admin
        if self.event.user_id == user.id:
            return True  # User is the creator of the event

        if not self.event.can_access(user):
            return False

        if self.event.orgc_id == user_org_id:
            return True

        if self.distribution == AttributeDistributionLevels.OWN_ORGANIZATION:
            return self.event.orgc_id == user_org_id
            # User is part of the same organisation as the organisation of the event and event is published
        elif self.distribution == AttributeDistributionLevels.COMMUNITY:
            return self.event.published  # Anyone has access if event is published
        elif self.distribution == AttributeDistributionLevels.CONNECTED_COMMUNITIES:
            return self.event.published  # Anyone has access if event is published
        elif self.distribution == AttributeDistributionLevels.ALL_COMMUNITIES:
            return self.event.published  # Anyone has access if event is published
        elif self.distribution == AttributeDistributionLevels.SHARING_GROUP:
            return self.sharing_group_id in user.org._sharing_group_ids
        elif self.distribution == AttributeDistributionLevels.INHERIT_EVENT:
            return True  # already checked event.can_access
        else:
            return False  # Something went wrong with the Distribution ID

    @can_access.expression
    def can_access(cls: Self, user: User | None) -> bool:
        """
        Checks if a user is allowed to see and access an attribute based on
        whether the attribute is part of the same group or organisation and or creating organisation and
        the publishing status of the attribute with
        consideration of the event the attribute is associated with.

         args:
            self: the attribute
            user: the user

        returns:
            true if the user has access permission
        """
        if user is None or user.role.check_permission(Permission.SITE_ADMIN):
            return True  # User is a Worker or Site Admin

        user_org_id = user.org_id

        condition = []
        condition.append(cls.event.has(Event.orgc_id == user_org_id))
        condition.append(cls.event.has(Event.user_id == user.id))
        condition.append(
            and_(
                cls.distribution == AttributeDistributionLevels.OWN_ORGANIZATION,
                cls.event.has(Event.orgc_id == user_org_id),
            )
        )
        condition.append(
            and_(
                cls.distribution.in_(
                    [
                        AttributeDistributionLevels.COMMUNITY,
                        AttributeDistributionLevels.CONNECTED_COMMUNITIES,
                        AttributeDistributionLevels.ALL_COMMUNITIES,
                    ]
                ),
                cls.event.has(Event.published),
            )
        )
        condition.append(
            and_(
                cls.distribution == AttributeDistributionLevels.SHARING_GROUP,
                cls.sharing_group_id.in_(user.org._sharing_group_ids),
            )
        )
        condition.append(cls.distribution == AttributeDistributionLevels.INHERIT_EVENT)
        return and_(cls.event.has(Event.can_access(user)), or_(*condition))

    @property
    def event_uuid(self: "Attribute") -> str:
        return self.event.uuid

    @hybrid_property
    def value(self: Self) -> str:
        if self.value2 == "":
            return self.value1
        return f"{self.value1}|{self.value2}"

    @value.setter  # type: ignore[no-redef]
    def value(self: Self, value: str) -> None:
        split = value.split("|", 1)
        self.value1 = split[0]
        if len(split) == 2:
            self.value2 = split[1]

    @value.comparator
    def value(cls: Self) -> AttributeComparator:
        return AttributeComparator(cls)


class AttributeTag(Base):
    __tablename__ = "attribute_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_id: Mapped[int] = mapped_column(Integer, ForeignKey(Attribute.id, ondelete="CASCADE"), index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey(Event.id, ondelete="CASCADE"), index=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey(Tag.id, ondelete="CASCADE"), index=True)
    local: Mapped[bool] = mapped_column(Boolean, default=False)
    relationship_type: Mapped[str | None] = mapped_column(String(191), default="")

    attribute = relationship("Attribute", back_populates="attributetags", lazy="raise_on_sql")
    tag = relationship("Tag", back_populates="attributetags", lazy="raise_on_sql")

    __table_args__ = {"extend_existing": True}


class AttributeMeta(AutoDictMeta):
    def __new__(cls: Type[type], clsname: str, bases: tuple, dct: dict) -> "AttributeMeta":
        key = clsname[len("Attribute") :]
        dct["default_category"] = default_category[mapper_safe_clsname_val[key]]
        dct["categories"] = categories[mapper_safe_clsname_val[key]]
        dct["default_to_ids"] = to_ids[mapper_safe_clsname_val[key]]
        dct["__mapper_args__"] = {"polymorphic_identity": mapper_safe_clsname_val[key]}
        return super().__new__(cls, clsname, bases, dct)  # type:ignore[misc]


for k, _ in mapper_safe_clsname_val.items():
    vars()["Attribute" + k] = AttributeMeta("Attribute" + k, (Attribute,), dict())
