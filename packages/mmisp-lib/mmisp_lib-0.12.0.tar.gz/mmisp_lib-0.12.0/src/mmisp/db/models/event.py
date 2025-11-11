from datetime import date, datetime
from typing import Self

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, String, Text, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.types import DBUUID, DateTimeEpoch
from mmisp.lib.distribution import EventDistributionLevels
from mmisp.lib.permissions import Permission
from mmisp.lib.uuid import uuid

from ..database import Base
from .organisation import Organisation

from .tag import Tag
from .user import User


class Event(Base, UpdateMixin, DictMixin["EventDict"]):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(DBUUID, unique=True, default=uuid, index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(Organisation.id), index=True)
    date: Mapped[date] = mapped_column(Date, default=datetime.utcnow)
    info: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    analysis: Mapped[int] = mapped_column(Integer)
    attribute_count: Mapped[int | None] = mapped_column(Integer, default=0)
    orgc_id: Mapped[int] = mapped_column(Integer, ForeignKey(Organisation.id), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTimeEpoch, default=0)
    distribution: Mapped[int] = mapped_column(Integer, default=0)
    sharing_group_id: Mapped[int] = mapped_column(Integer, index=True, default=0)
    proposal_email_lock: Mapped[bool] = mapped_column(Boolean, default=False)
    # This column was adedd as part of remove_column task
    first_publication: Mapped[int] = mapped_column(Integer, default=0)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    threat_level_id: Mapped[int] = mapped_column(Integer)
    publish_timestamp: Mapped[datetime] = mapped_column(DateTimeEpoch, default=0)
    sighting_timestamp: Mapped[int] = mapped_column(Integer, default=0)
    disable_correlation: Mapped[bool] = mapped_column(Boolean, default=False)
    extends_uuid: Mapped[str | None] = mapped_column(String(40), default="", index=True)
    protected: Mapped[bool | None] = mapped_column(Boolean, default=False)
    __table_args__ = (
        Index("uuid", "uuid", unique=True),
        {"extend_existing": True},
    )

    attributes = relationship("Attribute", back_populates="event")  # type:ignore[assignment,var-annotated]
    mispobjects = relationship("Object", back_populates="event")  # type:ignore[assignment,var-annotated]
    org = relationship(
        "Organisation", primaryjoin="Event.org_id == Organisation.id", back_populates="events", lazy="raise_on_sql"
    )  # type:ignore[assignment,var-annotated]
    orgc = relationship(
        "Organisation",
        primaryjoin="Event.orgc_id == Organisation.id",
        back_populates="events_created",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]
    creator = relationship("User", primaryjoin="Event.user_id == User.id", lazy="selectin")
    tags = relationship("Tag", secondary="event_tags", lazy="selectin", viewonly=True)
    eventtags = relationship(
        "EventTag", primaryjoin="Event.id == EventTag.event_id", lazy="raise_on_sql", viewonly=True
    )
    eventtags_galaxy = relationship(
        "EventTag",
        primaryjoin="and_(Event.id == EventTag.event_id, Tag.is_galaxy)",
        secondary="join(EventTag, Tag, EventTag.tag_id == Tag.id)",
        secondaryjoin="EventTag.tag_id == Tag.id",
        lazy="raise_on_sql",
        viewonly=True,
    )
    galaxy_tags = relationship(
        "Tag",
        secondary="event_tags",
        secondaryjoin="and_(EventTag.tag_id == Tag.id, Tag.is_galaxy)",
        lazy="raise_on_sql",
        overlaps="tags, events",
        viewonly=True,
    )
    sharing_group = relationship(
        "SharingGroup",
        primaryjoin="Event.sharing_group_id == SharingGroup.id",
        lazy="raise_on_sql",
        foreign_keys="Event.sharing_group_id",
    )

    async def add_tag(
        self: Self, db: AsyncSession, tag: Tag, local: bool = False, relationship_type: str | None = None
    ) -> "EventTag":
        """
        FIXME *Insert page break right here*
        """

        if tag.local_only:
            local = True
        event_tag: EventTag = EventTag(
            event=self, tag=tag, local=local, event_id=self.id, tag_id=tag.id, relationship_type=relationship_type
        )
        db.add(event_tag)
        await db.flush()
        await db.refresh(event_tag)
        return event_tag

    @hybrid_method
    def can_edit(self: Self, user: User) -> bool:
        """
        Checks if a user is allowed to modify an event based on
        whether he or someone of his organisation created the event.

        args:
            self: the event
            user: the user

        returns:
            true if the user has editing permission
        """
        return (
            user is not None  # user is a worker
            and (
                user.role.check_permission(Permission.SITE_ADMIN)
                or (user.id == self.user_id and user.role.check_permission(Permission.MODIFY))
                or (user.org_id == self.orgc_id and user.role.check_permission(Permission.MODIFY_ORG))
            )
        )

    @can_edit.expression
    def can_edit(cls: Self, user: User) -> bool:
        """
        Checks if a user is allowed to modify an event based on
        whether he or someone of his organisation created the event.

        args:
            self: the event
            user: the user

        returns:
            true if the user has editing permission
        """
        condition = []
        condition.append(user.role.check_permission(Permission.SITE_ADMIN))
        condition.append(and_(user.id == cls.user_id, user.role.check_permission(Permission.MODIFY)))
        condition.append(and_(user.org_id == cls.orgc_id, user.role.check_permission(Permission.MODIFY_ORG)))
        return and_(user is not None, or_(*condition))
        """
        return (
            user is not None  # user is not a worker
            and (
                user.role.check_permission(Permission.SITE_ADMIN)
                or (user.id == cls.user_id and user.role.check_permission(Permission.MODIFY))
                or (user.org_id == cls.org_id and user.role.check_permission(Permission.MODIFY_ORG))
                or (user.org_id == cls.orgc_id)
            )
        )
        """

    @hybrid_method
    def can_access(self: Self, user: User | None) -> bool:
        """
        Checks if a user is allowed to see and access an event based on
        whether the event is part of the same group or organisation and the publishing status of the event.

         args:
            self: the event
            user: the user

        returns:
            true if the user has access permission
        """
        if user is None or user.role.check_permission(Permission.SITE_ADMIN):
            return True  # User is a Worker or Site Admin

        user_org_id = user.org_id
        if user.id == self.user_id:
            return True  # User is the creator of the event

        if user_org_id == self.orgc_id:
            return True  # can always access own events

        if self.distribution == EventDistributionLevels.OWN_ORGANIZATION:
            return user_org_id == self.orgc_id
            # User is part of the same organisation as the organisation of the event and event is published
        elif self.distribution == EventDistributionLevels.COMMUNITY:
            return self.published  # Anyone has access if event is published
        elif self.distribution == EventDistributionLevels.CONNECTED_COMMUNITIES:
            return self.published  # Anyone has access if event is published
        elif self.distribution == EventDistributionLevels.ALL_COMMUNITIES:
            return self.published  # Anyone has access if event is published
        elif self.distribution == EventDistributionLevels.SHARING_GROUP:
            return self.sharing_group_id in user.org._sharing_group_ids and self.published
        else:
            return False  # Something went wrong with the Distribution ID

    @can_access.expression
    def can_access(cls: Self, user: User) -> bool:
        """
        Checks if a user is allowed to see and access an event based on
        whether the event is part of the same group or organisation and the publishing status of the event.

         args:
            self: the event
            user: the user

        returns:
            true if the user has access permission
        """
        user_org_id = user.org_id
        if user is None or user.role.check_permission(Permission.SITE_ADMIN):
            return True  # User is a Worker or Site Admin

        condition = []
        condition.append(user.id == cls.user_id)
        condition.append(user_org_id == cls.org_id)

        condition.append(
            and_(
                cls.distribution == EventDistributionLevels.OWN_ORGANIZATION,
                cls.org_id == user_org_id,
                cls.orgc_id == user_org_id,
            )
        )

        condition.append(
            and_(
                cls.distribution.in_(
                    [
                        EventDistributionLevels.COMMUNITY,
                        EventDistributionLevels.CONNECTED_COMMUNITIES,
                        EventDistributionLevels.ALL_COMMUNITIES,
                    ]
                ),
                cls.published,
            )
        )
        condition.append(
            and_(
                cls.distribution == EventDistributionLevels.SHARING_GROUP,
                cls.sharing_group_id.in_(user.org._sharing_group_ids),
                cls.published,
            )
        )

        return or_(*condition)


class EventReport(Base):
    __tablename__ = "event_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40), unique=True, default=uuid)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey(Event.id), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)

    content: Mapped[str | None] = mapped_column(Text)

    distribution: Mapped[int] = mapped_column(Integer, default=0)

    sharing_group_id: Mapped[int | None] = mapped_column(Integer)

    timestamp: Mapped[int] = mapped_column(Integer)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = ({"extend_existing": True},)


class EventTag(Base, DictMixin["EventTagDict"]):
    __tablename__ = "event_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey(Event.id, ondelete="CASCADE"), index=True)
    # event_uuid: Mapped[str] = mapped_column(String(40), ForeignKey(Event.uuid, ondelete="CASCADE"),
    #                                         unique=True, default=uuid)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey(Tag.id, ondelete="CASCADE"), index=True)
    local: Mapped[bool] = mapped_column(Boolean, default=False)
    relationship_type: Mapped[str | None] = mapped_column(String(191))

    event = relationship("Event", back_populates="eventtags", lazy="raise_on_sql", viewonly=True)
    tag = relationship("Tag", back_populates="eventtags", lazy="raise_on_sql", viewonly=True)
    __table_args__ = (Index("event_tag_uuid", event_id, tag_id, unique=False),)
