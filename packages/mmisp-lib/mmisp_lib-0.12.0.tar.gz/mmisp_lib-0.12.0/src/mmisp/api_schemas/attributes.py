from datetime import datetime
from typing import Annotated, Any, Optional, Self, Type

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from mmisp.api_schemas.attribute_common import CommonAttribute
from mmisp.lib.attributes import (
    AttributeCategories,
    AttributeType,
    default_category,
    inverted_categories,
    literal_valid_attribute_types,
    mapper_val_safe_clsname,
    to_ids,
)
from mmisp.lib.distribution import AttributeDistributionLevels, EventDistributionLevels


class GetAttributeTag(BaseModel):
    id: int
    name: str
    colour: str
    numerical_value: int | None = None
    is_galaxy: bool
    local: bool


class SearchAttributesObject(BaseModel):
    id: int
    distribution: AttributeDistributionLevels
    sharing_group_id: int


class SearchAttributesEvent(BaseModel):
    id: int
    org_id: int
    distribution: EventDistributionLevels
    user_id: int
    info: str
    orgc_id: int
    uuid: str
    publish_timestamp: datetime

    @field_serializer("publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())


class SearchAttributesAttributesDetails(BaseModel):
    id: int
    event_id: int | None = None
    object_id: int | None = None
    object_relation: str | None = None
    category: AttributeCategories
    type: str
    value: str
    to_ids: bool
    uuid: str
    timestamp: datetime
    distribution: AttributeDistributionLevels
    sharing_group_id: int | None = None
    comment: str | None = None
    deleted: bool
    disable_correlation: bool
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    event_uuid: str | None = None
    data: str | None = None
    Event: SearchAttributesEvent | None = None
    Object: SearchAttributesObject | None = None
    Tag: list[GetAttributeTag] | None = None

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())

    @field_validator("first_seen", mode="before")
    @classmethod
    def empty_string_to_none(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return None
        return value


class SearchAttributesAttributes(BaseModel):
    Attribute: list[SearchAttributesAttributesDetails]


class SearchAttributesResponse(BaseModel):
    response: SearchAttributesAttributes


class SearchAttributesModelOverridesBaseScoreConfig(BaseModel):
    estimative_language_confidence_in_analytic_judgment: Annotated[
        int, Field(alias="estimative-language:confidence-in-analytic-judgment")
    ]
    estimative_language_likelihood_probability: Annotated[
        int, Field(alias="estimative-language:likelihood-probability")
    ]
    phishing_psychological_acceptability: Annotated[int, Field(alias="phishing:psychological-acceptability")]
    phishing_state: Annotated[int, Field(alias="phishing:state")]


class SearchAttributesModelOverrides(BaseModel):
    lifetime: int
    decay_speed: int
    threshold: int
    default_base_score: int
    base_score_config: SearchAttributesModelOverridesBaseScoreConfig


class RestSearchFilter(BaseModel):
    value: str | None = None
    value1: str | None = None
    value2: str | None = None
    type: str | None = None
    category: AttributeCategories | None = None
    org: str | None = None
    tags: list[str] | None = None
    from_: str | None = None
    to: datetime | None = None
    last: int | None = None
    eventid: int | None = None
    published: bool | None = None
    to_ids: bool | None = None
    deleted: bool | None = None


class SearchAttributesBody(RestSearchFilter):
    model_config = ConfigDict(populate_by_name=True)

    returnFormat: str = "json"
    page: int | None = None
    limit: int | None = None
    with_attachments: Annotated[bool | None, Field(alias="withAttachments")] = None
    uuid: str | None = None
    publish_timestamp: datetime | None = None
    timestamp: datetime | None = None
    attribute_timestamp: datetime | None = None
    enforce_warninglist: Annotated[bool | None, Field(alias="enforceWarninglist")] = None
    event_timestamp: datetime | None = None
    threat_level_id: int | None = None
    eventinfo: str | None = None
    sharinggroup: list[str] | None = None
    decaying_model: Annotated[str | None, Field(alias="decayingModel")] = None
    score: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    include_event_uuid: bool | None = Field(alias="includeEventUuid", default=None)
    include_event_tags: Annotated[bool | None, Field(alias="includeEventTags")] = None
    include_proposals: Annotated[bool | None, Field(alias="includeProposals")] = None
    requested_attributes: list[str] | None = None
    include_context: Annotated[bool | None, Field(alias="includeContext")] = None
    headerless: bool | None = None
    include_warninglist_hits: Annotated[bool | None, Field(alias="includeWarninglistHits")] = None
    attack_galaxy: Annotated[str | None, Field(alias="attackGalaxy")] = None
    object_relation: str | None = None
    include_sightings: Annotated[bool | None, Field(alias="includeSightings")] = None
    include_correlations: Annotated[bool | None, Field(alias="includeCorrelations")] = None
    model_overrides: Annotated[SearchAttributesModelOverrides | None, Field(alias="modelOverrides")] = None
    include_decay_score: Annotated[bool | None, Field(alias="includeDecayScore")] = None
    include_full_model: Annotated[bool | None, Field(alias="includeFullModel")] = None
    exclude_decayed: Annotated[bool | None, Field(alias="excludeDecayed")] = None

    @field_serializer("timestamp", "publish_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())

    @field_validator("first_seen", mode="before")
    @classmethod
    def empty_string_to_none(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return None
        return value


class RestoreAttributeResponse(BaseModel):
    id: int
    event_id: int
    object_id: int
    object_relation: str
    category: str
    type: str
    value: str
    to_ids: bool
    uuid: str
    timestamp: datetime
    distribution: AttributeDistributionLevels
    sharing_group_id: int
    comment: str
    deleted: bool
    disable_correlation: bool
    first_seen: datetime | None
    last_seen: datetime | None
    event_uuid: str  # new
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())

    @field_validator("first_seen", mode="before")
    @classmethod
    def empty_string_to_none(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return None
        return value


class GetDescribeTypesAttributes(BaseModel):
    sane_defaults: dict = {}
    for _k, _v in to_ids.items():
        sane_defaults.update(
            {
                _k: {
                    "default_category": default_category[_k],
                    "to_ids": "1" if _v else "0",
                }
            }
        )

    types: list[str] = list(mapper_val_safe_clsname.keys())
    categories: list[str] = [member.value for member in AttributeCategories]
    category_type_mappings: dict = inverted_categories


class GetDescribeTypesResponse(BaseModel):
    result: GetDescribeTypesAttributes


class GetAttributeAttributes(CommonAttribute):
    event_uuid: str
    data: str | None = None
    Tag: list[GetAttributeTag] | None = None


class GetAttributeResponse(BaseModel):
    Attribute: GetAttributeAttributes
    model_config = ConfigDict(from_attributes=True)


class GetAllAttributesResponse(CommonAttribute):
    value1: str | None = None
    value2: str | None = None
    model_config = ConfigDict(from_attributes=True)


class EditAttributeTag(BaseModel):
    id: int
    name: str
    colour: str
    exportable: str
    user_id: int
    hide_tag: bool
    numerical_value: int
    is_galaxy: bool
    is_costum_galaxy: bool
    local_only: bool


class EditAttributeAttributes(BaseModel):
    id: int
    event_id: int
    object_id: int
    object_relation: str | None = None
    category: str
    type: str
    value: str
    to_ids: bool
    uuid: str
    timestamp: datetime
    distribution: AttributeDistributionLevels
    sharing_group_id: int
    comment: str | None = None
    deleted: bool
    disable_correlation: bool
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    Tag: list[EditAttributeTag]

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())

    @field_validator("first_seen", mode="before")
    @classmethod
    def empty_string_to_none(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return None
        return value


class EditAttributeResponse(BaseModel):
    Attribute: EditAttributeAttributes
    model_config = ConfigDict(from_attributes=True)


class EditAttributeBody(BaseModel):
    type: str | None = None
    value: str | None = None
    value1: str | None = None
    value2: str | None = None
    object_id: int | None = None
    object_relation: str | None = None
    category: str | None = None
    to_ids: bool | None = None
    uuid: str | None = None
    timestamp: datetime | None = None
    distribution: AttributeDistributionLevels | None = None
    sharing_group_id: int | None = None
    comment: str | None = None
    deleted: bool | None = None
    disable_correlation: bool | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())

    @field_validator("first_seen", mode="before")
    @classmethod
    def empty_string_to_none(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return None
        return value


class DeleteSelectedAttributeResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: str
    model_config = ConfigDict(from_attributes=True)


class DeleteAttributeResponse(BaseModel):
    message: str
    model_config = ConfigDict(from_attributes=True)


class AddRemoveTagAttributeResponse(BaseModel):
    saved: bool
    success: Optional[str] = None
    check_publish: Optional[bool] = None
    errors: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AddAttributeAttributes(CommonAttribute):
    value1: str
    value2: str
    attribute_tag: list[str] | None = Field(default_factory=list, alias="AttributeTag")


class AddAttributeResponse(BaseModel):
    Attribute: AddAttributeAttributes
    model_config = ConfigDict(from_attributes=True)


class AddAttributeBody(BaseModel):
    type: literal_valid_attribute_types  # type:ignore[valid-type]
    value: str | None = None
    value1: str | None = None
    value2: str | None = None
    event_id: int | None = None
    object_id: int | None = None
    object_relation: str | None = None
    category: str | None = None
    to_ids: bool | None = None
    uuid: str | None = None
    timestamp: datetime | None = None
    distribution: AttributeDistributionLevels | None = None
    sharing_group_id: int | None = None
    comment: str | None = None
    deleted: bool | None = None
    disable_correlation: bool | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    @model_validator(mode="after")
    def ensure_value_or_value1_is_set(self: Self) -> Self:
        if self.value is None:
            if self.value1 is None:
                raise ValueError("value or value1 has to be set")
            if self.value2 is not None:
                self.value = f"{self.value1}|{self.value2}"
            else:
                self.value = f"{self.value1}"
        return self

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())

    @field_validator("first_seen", "value", "value1", "value2", mode="before")
    @classmethod
    def empty_string_to_none(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def check_type_value(self: Self) -> Self:
        # get validator from attribute type
        at = AttributeType.map_dbkey_attributetype[self.type]
        validator = at.validator
        if not validator(self.value):
            raise ValueError(f"{self.value} is not compatible with attribute type {self.type}")

        return self


GetAttributeStatisticsTypesResponseAttrs = {x: Field(default=None) for x in mapper_val_safe_clsname.keys()}
GetAttributeStatisticsTypesResponseAttrs["__annotations__"] = {
    x: str | int | None for x in mapper_val_safe_clsname.keys()
}
GetAttributeStatisticsTypesResponse = type(  # type: ignore
    "GetAttributeStatisticsTypesResponse", (BaseModel,), GetAttributeStatisticsTypesResponseAttrs
)

GetAttributeStatisticsCategoriesResponseAttrs = {x.value: Field(default=None) for x in AttributeCategories}
GetAttributeStatisticsCategoriesResponseAttrs["__annotations__"] = {
    x.value: str | int | None for x in AttributeCategories
}
GetAttributeStatisticsCategoriesResponse = type(  # type: ignore
    "GetAttributeStatisticsCategoriesResponse", (BaseModel,), GetAttributeStatisticsCategoriesResponseAttrs
)
