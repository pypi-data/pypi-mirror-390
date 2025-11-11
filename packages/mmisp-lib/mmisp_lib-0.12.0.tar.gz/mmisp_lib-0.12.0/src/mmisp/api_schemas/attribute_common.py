from datetime import datetime
from typing import Any, Self, Type
from uuid import UUID

from pydantic import BaseModel, field_serializer, field_validator, model_validator

from mmisp.lib.attributes import (
    AttributeCategories,
    AttributeType,
    literal_valid_attribute_types,
)
from mmisp.lib.distribution import AttributeDistributionLevels


class CommonAttribute(BaseModel):
    id: int
    event_id: int
    object_id: int
    object_relation: str | None = None
    category: AttributeCategories
    type: literal_valid_attribute_types  # type:ignore[valid-type]
    value: str
    to_ids: bool
    uuid: UUID
    timestamp: datetime
    distribution: AttributeDistributionLevels
    sharing_group_id: int
    comment: str | None = None
    deleted: bool = False
    disable_correlation: bool = False
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    @field_serializer("timestamp")
    def serialize_timestamp(self: Self, timestamp: datetime, _: Any) -> int:
        return int(timestamp.timestamp())

    @field_serializer("first_seen", "last_seen")
    def serialize_timestamp_none(self: Self, timestamp: datetime, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())

    @field_validator("first_seen", mode="before")
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
