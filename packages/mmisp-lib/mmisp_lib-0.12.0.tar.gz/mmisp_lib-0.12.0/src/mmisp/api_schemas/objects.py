from datetime import datetime
from typing import Any, Self, Type

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from mmisp.api_schemas.attributes import AddAttributeBody, GetAllAttributesResponse
from mmisp.api_schemas.events import ObjectEventResponse
from mmisp.lib.distribution import AttributeDistributionLevels


class ObjectSearchBody(BaseModel):
    object_name: str | None = None
    object_template_uuid: str | None = None
    object_template_version: int | None = None
    event_id: int | None = None
    category: str | None = None
    comment: str | None = None
    first_seen: int | None = None
    last_seen: int | None = None
    quick_filter: str | None = None
    timestamp: datetime | None = None
    event_info: str | None = None
    from_: str | None = None  # 'from' is a reserved word in Python, so an underscore is added
    to: str | None = None
    date: str | None = None
    last: str | None = None
    event_timestamp: datetime | None = None
    org_id: int | None = None
    uuid: str | None = None
    value1: str | None = None
    value2: str | None = None
    type: str | None = None
    object_relation: str | None = None
    attribute_timestamp: datetime | None = None
    to_ids: bool | None = None
    published: bool | None = None
    deleted: bool | None = None
    return_format: str | None = "json"
    limit: str | None = "25"

    @field_validator("limit")
    @classmethod
    def check_limit(cls: Type["ObjectSearchBody"], value: Any) -> str:  # noqa: ANN101
        if value:
            try:
                limit_int = int(value)
            except ValueError:
                raise ValueError("'limit' must be a valid integer")

            if not 1 <= limit_int <= 500:
                raise ValueError("'limit' must be between 1 and 500")
        return value

    @field_serializer("timestamp", "event_timestamp", "attribute_timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class ObjectWithAttributesResponse(BaseModel):
    id: int
    uuid: str
    name: str
    meta_category: str | None = None
    description: str | None = None
    template_uuid: str | None = None
    template_version: int | None = None
    event_id: int | None = None
    timestamp: datetime | None = None
    distribution: AttributeDistributionLevels | None = None
    sharing_group_id: int | None = None  # is none if distribution is not 4, see validator
    comment: str | None = None
    deleted: bool | None = None
    first_seen: int | None = None
    last_seen: int | None = None
    attributes: list[GetAllAttributesResponse] | None = Field(alias="Attribute", default=None)
    Event: ObjectEventResponse | None = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @model_validator(mode="after")
    def check_sharing_group_id(self: Self) -> Self:
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        if self.distribution not in [
            AttributeDistributionLevels.SHARING_GROUP,
            AttributeDistributionLevels.INHERIT_EVENT,
        ]:
            if self.sharing_group_id is not None and self.sharing_group_id != 0:
                raise ValueError("Distribution does not allow to set a sharing group")
        return self

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class ObjectResponse(BaseModel):
    Object: ObjectWithAttributesResponse


class ObjectSearchResponse(BaseModel):
    response: list[ObjectResponse]


class ObjectCreateBody(BaseModel):
    name: str | None = None
    meta_category: str | None = None
    description: str | None = None
    distribution: AttributeDistributionLevels | None = None
    sharing_group_id: int = 0
    comment: str = ""
    deleted: bool | None = None
    first_seen: int | None = None
    last_seen: int | None = None
    Attribute: list[AddAttributeBody] | None = None
