from datetime import datetime
from typing import Any, List, Self, Type, Union

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_serializer, field_validator
from typing_extensions import Annotated


class SearchGetAuthKeysResponseItemUser(BaseModel):
    id: int
    email: str


class CreatedExpiration(BaseModel):
    created: datetime
    expiration: datetime

    @field_serializer("created", "expiration")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class ViewAuthKeyResponseWrapper(CreatedExpiration):
    id: int
    uuid: str
    authkey_start: str
    authkey_end: str
    read_only: bool
    user_id: int
    comment: str
    allowed_ips: list[str] | None = None
    unique_ips: list[str] | None = []


class ViewAuthKeysResponse(BaseModel):
    AuthKey: ViewAuthKeyResponseWrapper
    User: SearchGetAuthKeysResponseItemUser


class SearchGetAuthKeysResponseItemAuthKey(CreatedExpiration):
    id: int
    uuid: str
    authkey_start: str
    authkey_end: str
    read_only: bool
    user_id: int
    comment: str | None = None
    allowed_ips: list[str] | None = None
    unique_ips: list[str] | None = []


class SearchGetAuthKeysResponseAuthKey(CreatedExpiration):
    id: int
    uuid: str
    authkey_start: str
    authkey_end: str
    read_only: bool
    user_id: int
    comment: str | None = None
    allowed_ips: list[str] | None = None
    unique_ips: list[str] | None = []
    last_used: str | None = None


class SearchGetAuthKeysResponseItem(BaseModel):
    AuthKey: SearchGetAuthKeysResponseItemAuthKey
    User: SearchGetAuthKeysResponseItemUser
    model_config = ConfigDict(from_attributes=True)


class SearchGetAuthKeysResponse(BaseModel):
    AuthKey: SearchGetAuthKeysResponseAuthKey
    User: SearchGetAuthKeysResponseItemUser
    model_config = ConfigDict(from_attributes=True)


class SearchAuthKeyBody(BaseModel):
    page: PositiveInt = 1
    limit: Annotated[int, Field(gt=0, lt=500)] = 25  # type: ignore
    id: int | None = None
    uuid: str | None = None
    authkey_start: str | None = None
    authkey_end: str | None = None
    created: datetime | None = None
    expiration: datetime | None = None
    read_only: bool | None = None
    user_id: int | None = None
    comment: str | None = None
    allowed_ips: str | list[str] | None = None
    last_used: str | None = None  # deprecated


class EditAuthKeyResponseAuthKey(CreatedExpiration):
    id: int
    uuid: str
    authkey_start: str
    authkey_end: str
    read_only: bool
    user_id: int
    comment: str
    allowed_ips: str | None = None


class EditAuthKeyResponseCompleteAuthKey(CreatedExpiration):
    id: int
    uuid: str
    authkey_start: str
    authkey_end: str
    read_only: bool
    user_id: int
    comment: str
    allowed_ips: str | None = None
    unique_ips: list[str] | None = None


class EditAuthKeyResponseUser(BaseModel):
    id: int
    org_id: int


class EditAuthKeyResponse(BaseModel):
    AuthKey: EditAuthKeyResponseAuthKey
    User: EditAuthKeyResponseUser


class EditAuthKeyResponseCompl(BaseModel):
    AuthKey: EditAuthKeyResponseCompleteAuthKey
    User: EditAuthKeyResponseUser


class EditAuthKeyBody(BaseModel):
    read_only: bool | None = None
    comment: str | None = None
    allowed_ips: Union[str, List[str]] | None = None
    expiration: datetime | None = None

    @field_validator("expiration", mode="before")
    @classmethod
    def empty_string_to_int_null(cls: Type[Self], value: Any) -> Any:
        if value == "":
            return 0
        return value

    @field_validator("allowed_ips", mode="before")
    @classmethod
    def ensure_list(cls: Type[Self], v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [v]
        return v


class AddAuthKeyResponseAuthKey(CreatedExpiration):
    id: int
    uuid: str
    authkey_start: str
    authkey_end: str
    expiration: datetime | None
    read_only: bool
    user_id: int
    comment: str | None = None
    allowed_ips: list[str] | None = None
    unique_ips: list[str]
    authkey_raw: str


class AddAuthKeyResponse(BaseModel):
    AuthKey: AddAuthKeyResponseAuthKey


class AddAuthKeyBody(BaseModel):
    uuid: str | None = None
    read_only: bool | None = None
    user_id: int | None = None
    comment: str | None = None
    allowed_ips: list[str] | None = None
    expiration: int | str | None = 0
