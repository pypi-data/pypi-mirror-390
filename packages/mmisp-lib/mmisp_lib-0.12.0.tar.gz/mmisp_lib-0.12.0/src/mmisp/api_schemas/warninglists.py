from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from mmisp.lib.attributes import literal_valid_attribute_types


class WarninglistCategory(StrEnum):
    FALSE_POSITIVE = "False positive"
    KNOWN_IDENTIFIER = "Known identifier"


class WarninglistListType(StrEnum):
    CIDR = "cidr"
    HOSTNAME = "hostname"
    STRING = "string"
    SUBSTRING = "substring"
    REGEX = "regex"


class WarninglistTypeResponse(BaseModel):
    id: int
    type: str
    warninglist_id: int


class WarninglistEntryResponse(BaseModel):
    id: int
    value: str = Field(max_length=65535)
    warninglist_id: int
    comment: str | None = None


class WarninglistBaseResponse(BaseModel):
    id: int
    name: str = Field(max_length=255)
    type: str
    description: str = Field(max_length=65535)
    version: int
    enabled: bool
    default: bool
    category: str


class WarninglistAttributesResponse(WarninglistBaseResponse):
    WarninglistEntry: list[WarninglistEntryResponse] | None = None
    WarninglistType: list[WarninglistTypeResponse] | None = None


class WarninglistResponse(BaseModel):
    Warninglist: WarninglistAttributesResponse
    model_config = ConfigDict(from_attributes=True)


class WarninglistAttributes(WarninglistBaseResponse):
    warninglist_entry_count: int
    valid_attributes: str


class ToggleEnableWarninglistsResponse(BaseModel):
    saved: bool
    success: str | None = None
    errors: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ToggleEnableWarninglistsBody(BaseModel):
    id: int | list[int]
    name: str | list[str]
    enabled: bool
    model_config = ConfigDict(from_attributes=True)


class GetSelectedWarninglistsBody(BaseModel):
    value: str | None = None
    enabled: bool | None = None
    model_config = ConfigDict(from_attributes=True)


class WarninglistsResponse(BaseModel):
    Warninglist: WarninglistAttributes


class GetSelectedAllWarninglistsResponse(BaseModel):
    Warninglists: list[WarninglistsResponse]
    model_config = ConfigDict(from_attributes=True)


class DeleteWarninglistResponse(BaseModel):
    saved: bool
    success: bool
    id: int
    name: str
    message: str
    url: str
    model_config = ConfigDict(from_attributes=True)


class CreateWarninglistBody(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: WarninglistListType
    description: str = Field(min_length=1, max_length=65535)
    enabled: bool
    default: bool
    category: WarninglistCategory
    valid_attributes: list[literal_valid_attribute_types]  # type:ignore[valid-type]
    values: str = Field(min_length=1, max_length=65535)
    model_config = ConfigDict(from_attributes=True)


class NameWarninglist(BaseModel):
    id: int
    name: str
    matched: str


class CheckValueResponse(BaseModel):
    value: list[NameWarninglist]
    model_config = ConfigDict(from_attributes=True)


class CheckValueWarninglistsBody(BaseModel):
    value: str
    model_config = ConfigDict(from_attributes=True)
