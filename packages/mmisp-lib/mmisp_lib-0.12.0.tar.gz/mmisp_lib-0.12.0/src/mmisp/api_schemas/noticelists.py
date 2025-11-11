from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict


class NoticelistAttributes(BaseModel):
    id: int
    name: str
    expanded_name: str
    ref: list[str]
    geographical_area: list[str]
    version: int
    enabled: bool


class Data(BaseModel):
    scope: str | list[str] | None = None
    field: str | list[str] | None = None
    value: str | list[str] | None = None
    tags: str | list[str] | None = None
    message: str | Any


class NoticelistEntryResponse(BaseModel):
    id: int
    noticelist_id: int
    data: Data


class NoticelistAttributesResponse(NoticelistAttributes):
    NoticelistEntry: Sequence[NoticelistEntryResponse]


class GetAllNoticelists(BaseModel):
    Noticelist: NoticelistAttributes
    model_config = ConfigDict(from_attributes=True)


class NoticelistResponse(BaseModel):
    Noticelist: NoticelistAttributesResponse
    model_config = ConfigDict(from_attributes=True)
