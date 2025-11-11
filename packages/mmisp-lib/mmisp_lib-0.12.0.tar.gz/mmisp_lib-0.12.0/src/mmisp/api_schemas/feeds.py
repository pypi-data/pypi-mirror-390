from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mmisp.lib.distribution import AttributeDistributionLevels


class FeedUpdateBody(BaseModel):
    name: str | None = None
    provider: str | None = None
    url: str | None = None
    rules: str | None = None
    enabled: bool | None = None
    distribution: int | None = None
    sharing_group_id: int | None = None
    tag_id: int | None = None
    default: bool | None = None
    source_format: str | None = None
    fixed_event: bool | None = None
    delta_merge: bool | None = None
    event_id: int | None = None
    publish: bool | None = None
    override_ids: bool | None = None
    settings: str | None = None
    input_source: str | None = None
    delete_local_file: bool | None = None
    lookup_visible: bool | None = None
    headers: str | None = None
    caching_enabled: bool | None = None
    force_to_ids: bool | None = None
    orgc_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class FeedToggleBody(BaseModel):
    enable: bool
    model_config = ConfigDict(from_attributes=True)


class FeedAttributesResponse(BaseModel):
    id: int
    name: str
    provider: str
    url: str
    rules: str | None = None
    enabled: bool | None = None
    distribution: int
    sharing_group_id: int | None = None
    tag_id: int
    default: bool | None = None
    source_format: str | None = None
    fixed_event: bool
    delta_merge: bool
    event_id: int
    publish: bool
    override_ids: bool
    settings: str | None = None
    input_source: str
    delete_local_file: bool | None = None
    lookup_visible: bool | None = None
    headers: str | None = None
    caching_enabled: bool
    force_to_ids: bool
    orgc_id: int

    @model_validator(mode="after")
    def check_sharing_group_id(self: Self) -> Self:
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        if self.distribution not in [
            None,
            AttributeDistributionLevels.SHARING_GROUP,
            AttributeDistributionLevels.INHERIT_EVENT,
        ]:
            if self.sharing_group_id is not None and self.sharing_group_id != 0:
                raise ValueError(
                    "Distribution does not allow to set a sharing group, "
                    + "name: %s, distribution: %s, sharing_group_id: ",
                    (self.name, self.distribution, self.sharing_group_id),
                )
        return self


class FeedResponse(BaseModel):
    Feed: FeedAttributesResponse
    model_config = ConfigDict(from_attributes=True)


class FeedFetchResponse(BaseModel):
    result: str
    model_config = ConfigDict(from_attributes=True)


class FeedEnableDisableResponse(BaseModel):
    name: str
    message: str
    url: str
    model_config = ConfigDict(from_attributes=True)


class FeedCreateBody(BaseModel):
    name: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    url: str = Field(min_length=1)
    rules: str | None = None
    enabled: bool | None = None
    distribution: int | None = None
    sharing_group_id: int | None = None
    tag_id: int | None = None
    default: bool | None = None
    source_format: str | None = None
    fixed_event: bool | None = None
    delta_merge: bool | None = None
    event_id: int | None = None
    publish: bool | None = None
    override_ids: bool | None = None
    settings: str | None = None
    input_source: str | None = None
    delete_local_file: bool | None = None
    lookup_visible: bool | None = None
    headers: str | None = None
    caching_enabled: bool | None = None
    force_to_ids: bool | None = None
    orgc_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class FeedCacheResponse(BaseModel):
    name: str
    message: str
    url: str
    saved: bool
    success: bool
    model_config = ConfigDict(from_attributes=True)
