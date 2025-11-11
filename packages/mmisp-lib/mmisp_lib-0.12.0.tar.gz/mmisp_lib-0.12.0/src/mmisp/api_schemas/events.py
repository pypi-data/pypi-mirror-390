import uuid
from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, Field, PositiveInt, field_serializer
from typing_extensions import Annotated

from mmisp.api_schemas.attribute_common import CommonAttribute
from mmisp.api_schemas.galaxy_common import CommonGalaxy, CommonGalaxyCluster, GalaxyClusterMeta
from mmisp.api_schemas.organisations import Organisation
from mmisp.api_schemas.sharing_groups import EventSharingGroupResponse, MinimalSharingGroup
from mmisp.lib.distribution import AttributeDistributionLevels, EventDistributionLevels


class GetAllEventsGalaxyClusterGalaxy(CommonGalaxy):
    pass


class AddEditGetEventGalaxyClusterRelationTag(BaseModel):
    id: int
    name: str
    colour: str
    exportable: bool
    org_id: int
    user_id: int
    hide_tag: bool
    numerical_value: int
    is_galaxy: bool
    is_custom_galaxy: bool
    local_only: bool


class AddEditGetEventGalaxyClusterRelation(BaseModel):
    id: int
    galaxy_cluster_id: int
    referenced_galaxy_cluster_id: int
    referenced_galaxy_cluster_uuid: str
    referenced_galaxy_cluster_type: str
    galaxy_cluster_uuid: str
    distribution: AttributeDistributionLevels
    sharing_group_id: int | None = None
    default: bool
    Tag: list[AddEditGetEventGalaxyClusterRelationTag] = []


class AddEditGetEventGalaxyClusterMeta(GalaxyClusterMeta):
    pass


class GetAllEventsGalaxyCluster(CommonGalaxyCluster):
    Galaxy: GetAllEventsGalaxyClusterGalaxy


class AddEditGetEventGalaxyCluster(CommonGalaxyCluster):
    meta: dict[str, list]

    GalaxyClusterRelation: list[AddEditGetEventGalaxyClusterRelation] = []
    Org: Organisation | None = None
    Orgc: Organisation | None = None
    attribute_tag_id: int | None = None
    event_tag_id: int | None = None


class AddEditGetEventGalaxy(CommonGalaxy):
    GalaxyCluster: list[AddEditGetEventGalaxyCluster] = []


class FreeTextImportWorkerData(BaseModel):
    data: str


class FreeTextImportWorkerUser(BaseModel):
    user_id: int


class FreeTextImportWorkerBody(BaseModel):
    user: FreeTextImportWorkerUser
    data: FreeTextImportWorkerData


class AddAttributeViaFreeTextImportEventResponse(BaseModel):
    comment: str | None = None
    value: str
    original_value: str
    to_ids: str
    type: str
    category: str
    distribution: AttributeDistributionLevels


class AddAttributeViaFreeTextImportEventAttributes(BaseModel):
    value: str


class AddAttributeViaFreeTextImportEventBody(BaseModel):
    Attribute: AddAttributeViaFreeTextImportEventAttributes


class AddEditGetEventOrg(BaseModel):
    id: int
    name: str
    uuid: str | None = None
    local: bool | None = None


class AddEditGetEventTag(BaseModel):
    id: int
    name: str
    colour: str
    exportable: bool
    user_id: int
    hide_tag: bool
    numerical_value: int | None = None
    is_galaxy: bool
    is_custom_galaxy: bool
    local_only: bool
    local: bool
    relationship_type: bool | str | None = None


class AddEditGetEventAttribute(CommonAttribute):
    Galaxy: list[AddEditGetEventGalaxy] = []
    sharing_group: EventSharingGroupResponse | None = Field(alias="SharingGroup", default=None)
    ShadowAttribute: list[str] = []
    Tag: list[AddEditGetEventTag] = []

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class AddEditGetEventShadowAttribute(BaseModel):
    value: str
    to_ids: bool
    type: str
    category: str


class AddEditGetEventEventReport(BaseModel):
    id: int
    uuid: str
    event_id: int
    name: str
    content: str
    distribution: AttributeDistributionLevels
    sharing_group_id: int
    timestamp: datetime
    deleted: bool

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class AddEditGetEventObject(BaseModel):
    id: int
    name: str
    meta_category: str
    description: str
    template_uuid: str
    template_version: str | int
    event_id: int
    uuid: str
    timestamp: datetime
    distribution: AttributeDistributionLevels
    sharing_group_id: int
    comment: str
    deleted: bool
    first_seen: str | None = None
    last_seen: str | None = None
    ObjectReference: list[str] = []
    Attribute: list[AddEditGetEventAttribute] = []

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class AddEditGetEventRelatedEventAttributesOrg(BaseModel):
    id: int
    name: str
    uuid: str


class AddEditGetEventRelatedEventAttributes(BaseModel):
    id: int
    date: str
    threat_level_id: int
    info: str
    published: str
    uuid: str
    analysis: str | int
    timestamp: datetime
    distribution: AttributeDistributionLevels
    org_id: int
    orgc_id: int
    Org: AddEditGetEventRelatedEventAttributesOrg
    Orgc: AddEditGetEventRelatedEventAttributesOrg

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class AddEditGetEventRelatedEvent(BaseModel):
    Event: AddEditGetEventRelatedEventAttributes
    RelationshipInbound: list


class AddEditGetEventDetails(BaseModel):
    id: int | None = None
    orgc_id: int
    org_id: int
    date: str
    threat_level_id: int
    info: str
    published: bool
    uuid: str
    attribute_count: int
    analysis: str | int
    timestamp: datetime | None = None
    distribution: EventDistributionLevels
    proposal_email_lock: bool
    locked: bool
    publish_timestamp: datetime | None = None
    sharing_group_id: int | None = None
    disable_correlation: bool
    extends_uuid: str | None = None
    protected: bool | None = None
    event_creator_email: str | None = None
    Org: AddEditGetEventOrg | None = None
    Orgc: AddEditGetEventOrg | None = None
    Attribute: list[AddEditGetEventAttribute] = []
    ShadowAttribute: list[AddEditGetEventShadowAttribute] = []
    RelatedEvent: list[AddEditGetEventRelatedEvent] = []
    Galaxy: list[AddEditGetEventGalaxy] = []
    Object: list[AddEditGetEventObject] = []
    EventReport: list[AddEditGetEventEventReport] = []
    CryptographicKey: list[str] = []
    Tag: list[AddEditGetEventTag] = []
    sharing_group: EventSharingGroupResponse | None = Field(alias="SharingGroup", default=None)

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class AddEditGetEventResponse(BaseModel):
    Event: AddEditGetEventDetails


class GetAllEventsOrg(BaseModel):
    id: int
    name: str
    uuid: str | None = None


class UnpublishEventResponse(BaseModel):
    saved: bool | None = None
    success: bool | None = None
    name: str
    message: str
    url: str
    id: uuid.UUID | int | None = None


class SearchEventsResponse(BaseModel):
    response: list[AddEditGetEventResponse]


class SearchEventsBody(BaseModel):
    returnFormat: str
    page: int | None = None
    limit: int | None = None
    value: str | None = None
    type: str | None = None
    category: str | None = None
    org: str | None = None
    tags: list[str] | None = None
    event_tags: list[str] | None = None
    searchall: str | None = None
    from_: str | None = None
    to: str | None = None
    last: int | None = None
    eventid: int | None = None
    withAttachments: bool | None = None
    sharinggroup: list[str] | None = None
    metadata: bool | None = None
    uuid: str | None = None
    publish_timestamp: datetime | None = None
    timestamp: datetime | None = None
    published: bool | None = None
    enforceWarninglist: bool | None = None
    sgReferenceOnly: bool | None = None
    requested_attributes: list[str] | None = None
    includeContext: bool | None = None
    headerless: bool | None = None
    includeWarninglistHits: bool | None = None
    attackGalaxy: str | None = None
    to_ids: bool | None = None
    deleted: bool | None = None
    excludeLocalTags: bool | None = None
    date: str | None = None
    includeSightingdb: bool | None = None
    tag: str | None = None
    object_relation: str | None = None
    threat_level_id: int | None = None

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class PublishEventResponse(BaseModel):
    saved: bool | None = None
    success: bool | None = None
    name: str
    message: str
    url: str
    id: uuid.UUID | int | None = None


class GetAllEventsEventTagTag(BaseModel):
    id: uuid.UUID | int
    name: str
    colour: str
    is_galaxy: bool


class IndexEventsEventTag(BaseModel):
    id: uuid.UUID | int
    event_id: int
    tag_id: int
    local: bool
    relationship_type: bool | str | None = None
    Tag: GetAllEventsEventTagTag


class GetAllEventsEventTag(IndexEventsEventTag):
    pass


class IndexEventsAttributes(BaseModel):
    id: int
    org_id: int
    date: str
    info: str
    uuid: str
    published: bool
    analysis: str | int
    attribute_count: int
    orgc_id: int
    timestamp: datetime
    distribution: AttributeDistributionLevels
    sharing_group_id: int
    proposal_email_lock: bool
    locked: bool
    threat_level_id: int
    publish_timestamp: datetime
    sighting_timestamp: int
    disable_correlation: bool
    extends_uuid: str
    protected: bool | None = None
    Org: GetAllEventsOrg
    Orgc: GetAllEventsOrg
    GalaxyCluster: list[GetAllEventsGalaxyCluster] = []
    EventTag: list[IndexEventsEventTag] = []

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class IndexEventsBody(BaseModel):
    page: PositiveInt | None = None
    limit: Annotated[int, Field(gt=0, lt=500)] | None = None  # type: ignore
    sort: int | None = None
    direction: int | None = None
    minimal: bool | None = None
    attribute: str | None = None
    eventid: int | None = None
    datefrom: str | None = None
    dateuntil: str | None = None
    org: str | None = None
    eventinfo: str | None = None
    tag: str | None = None
    tags: list[str] | None = None
    distribution: AttributeDistributionLevels | None = None
    sharinggroup: str | None = None
    analysis: str | int | None = None
    threatlevel: str | None = None
    email: str | None = None
    hasproposal: str | None = None
    timestamp: datetime | None = None
    publish_timestamp: datetime | None = None
    published: bool | None = None
    searchDatefrom: str | None = None
    searchDateuntil: str | None = None

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class ObjectEventResponse(BaseModel):
    id: uuid.UUID | int
    info: str
    org_id: int | None = None
    orgc_id: int | None = None


class GetAllEventsResponse(BaseModel):
    id: int
    org_id: int  # owner org
    distribution: AttributeDistributionLevels
    info: str
    orgc_id: int  # creator org
    uuid: str
    date: str
    published: bool
    analysis: str | int
    attribute_count: int
    timestamp: datetime
    sharing_group_id: int
    proposal_email_lock: bool
    locked: bool
    threat_level_id: int
    publish_timestamp: datetime
    sighting_timestamp: int
    disable_correlation: bool
    extends_uuid: str
    event_creator_email: str | None = None  # omitted
    protected: bool | None = None
    SharingGroup: MinimalSharingGroup | None = None
    Org: GetAllEventsOrg
    Orgc: GetAllEventsOrg
    GalaxyCluster: list[GetAllEventsGalaxyCluster]
    EventTag: list[GetAllEventsEventTag]

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class EditEventBody(BaseModel):
    info: str | None = None
    org_id: int | None = None
    distribution: AttributeDistributionLevels | None = None
    orgc_id: int | None = None
    uuid: str | None = None
    date: str | None = None
    published: bool | None = None
    analysis: str | int | None = None
    attribute_count: int | None = None
    timestamp: datetime | None = None
    sharing_group_id: int | None = None
    proposal_email_lock: bool | None = None
    locked: bool | None = None
    threat_level_id: int | None = None
    publish_timestamp: datetime | None = None
    sighting_timestamp: int | None = None
    disable_correlation: bool | None = None
    extends_uuid: str | None = None
    event_creator_email: str | None = None
    protected: bool | None = None
    cryptographic_key: str | None = None

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class DeleteEventResponse(BaseModel):
    saved: bool
    success: bool | None = None
    name: str
    message: str
    url: str
    id: uuid.UUID | int
    errors: str | None = None


class AddRemoveTagEventsResponse(BaseModel):
    saved: bool
    success: str | None = None
    check_publish: bool | None = None
    errors: str | None = None


class AddEventBody(BaseModel):
    info: str
    org_id: int | None = None
    distribution: AttributeDistributionLevels | None = None
    orgc_id: int | None = None
    uuid: str | None = None
    date: str | None = None
    published: bool | None = None
    analysis: str | int | None = None
    attribute_count: int | None = None
    timestamp: datetime | None = None
    sharing_group_id: int | None = None
    proposal_email_lock: bool | None = None
    locked: bool | None = None
    threat_level_id: int | None = None
    publish_timestamp: datetime | None = None
    sighting_timestamp: int | None = None
    disable_correlation: bool | None = None
    extends_uuid: str | None = None
    protected: bool | None = None

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class AddEventTag(BaseModel):
    name: str
